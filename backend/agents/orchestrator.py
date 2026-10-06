import uuid
from typing import List, Dict, Any, Optional
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisResult, AnalysisPlan, AnalysisStatus, CanonicalResult
from backend.models.verification import VerificationResult, CheckStatus
from backend.models.dataset import DatasetArtifact
from backend.agents.planner import QueryPlanner
from backend.agents.analyst import DataAnalystAgent
from backend.agents.document_agent import DocumentAgent
from backend.codegen.generator import CodeGeneratorService
from backend.execution.sandbox import SandboxExecutionEnvironment
from backend.verification.result_checker import ResultChecker
from backend.verification.reproducibility import ReproducibilityVerifier
from backend.verification.evidence import EvidenceAccumulator
from backend.verification.confidence import ConfidenceCalculator
from backend.services.storage import storage_service
from backend.config import settings

class AnalysisOrchestrator:
    """Central orchestrator enforcing strict status transitions, dataset artifact scoping, and proof-carrying verification."""

    def __init__(
        self,
        planner: QueryPlanner,
        analyst: DataAnalystAgent,
        document_agent: DocumentAgent,
        code_generator: CodeGeneratorService,
        sandbox: SandboxExecutionEnvironment
    ):
        self.planner = planner
        self.analyst = analyst
        self.document_agent = document_agent
        self.code_generator = code_generator
        self.sandbox = sandbox

    def process_analysis(self, request: AnalysisRequest) -> AnalysisResult:
        analysis_id = f"ans_{uuid.uuid4().hex[:12]}"

        # 1. Status: RECEIVED
        # Retrieve explicit Dataset Artifacts
        selected_artifacts: List[DatasetArtifact] = []
        dataset_schemas: List[Dict[str, Any]] = []
        quality_warnings: List[Dict[str, Any]] = []

        for ds_id in request.selected_datasets:
            artifact = storage_service.get_dataset_artifact(ds_id)
            if artifact:
                selected_artifacts.append(artifact)
                dataset_schemas.append(artifact.profile.model_dump())
                quality_warnings.extend([w.model_dump() for w in artifact.profile.quality_warnings])

        document_summaries = []
        for doc_id in request.selected_documents:
            meta = storage_service.get_document_metadata(doc_id)
            if meta:
                document_summaries.append(meta.model_dump())

        # 2. Status: PLANNED
        plan: AnalysisPlan = self.planner.create_plan(request.question, dataset_schemas, document_summaries)

        # Refusal Check
        if plan.is_unanswerable or plan.query_type == "unanswerable":
            refusal_reason = plan.refusal_reason or "insufficient_data"
            v_res = VerificationResult(
                executed=CheckStatus.NOT_APPLICABLE,
                execution_success=CheckStatus.NOT_APPLICABLE,
                output_present=CheckStatus.NOT_APPLICABLE,
                output_valid=CheckStatus.NOT_APPLICABLE,
                reproducible=CheckStatus.NOT_APPLICABLE,
                status="REFUSED",
                confidence_score=0.0
            )
            result = AnalysisResult(
                analysis_id=analysis_id,
                question=request.question,
                answer=f"Question refused: {refusal_reason}. The available datasets/documents do not support this query reliably.",
                status=AnalysisStatus.REFUSED,
                code=None,
                expected_result_type="refusal",
                refusal_reason=refusal_reason,
                verification=v_res,
                confidence=0.0
            )
            storage_service.save_analysis_run(analysis_id, request.question, AnalysisStatus.REFUSED, result.model_dump())
            return result

        # Model Not Configured Check
        if settings.LLM_PROVIDER.lower() not in ["mock"] or settings.CODE_GEN_PROVIDER.lower() not in ["mock"]:
            v_res = VerificationResult(status="UNVERIFIED", confidence_score=0.0)
            result = AnalysisResult(
                analysis_id=analysis_id,
                question=request.question,
                answer="Configured AI model provider is pending GPU installation on this environment.",
                status=AnalysisStatus.MODEL_NOT_CONFIGURED,
                verification=v_res,
                confidence=0.0
            )
            storage_service.save_analysis_run(analysis_id, request.question, AnalysisStatus.MODEL_NOT_CONFIGURED, result.model_dump())
            return result

        # Document Retrieval & Evidence
        doc_chunks = []
        if request.selected_documents or plan.needs_retrieval or plan.query_type in ["document_retrieval", "hybrid"]:
            doc_chunks = self.document_agent.retrieve_supporting_chunks(request.question, top_k=3)

        # 3. Status: CODE_GENERATED & CODE_VALIDATED
        gen_res = self.code_generator.generate_and_validate(request.question, dataset_schemas, quality_warnings)
        code = gen_res.get("code", "")
        expected_type = gen_res.get("expected_result_type", "number")

        if not gen_res.get("is_valid", False):
            v_res = VerificationResult(
                executed=CheckStatus.FAIL,
                execution_success=CheckStatus.FAIL,
                status="VERIFICATION_FAILED",
                errors=gen_res.get("validation_errors", [])
            )
            result = AnalysisResult(
                analysis_id=analysis_id,
                question=request.question,
                answer="Generated analytical code failed static AST security validation.",
                status=AnalysisStatus.VERIFICATION_FAILED,
                code=code,
                verification=v_res,
                confidence=0.0,
                warnings=gen_res.get("validation_errors", [])
            )
            storage_service.save_analysis_run(analysis_id, request.question, AnalysisStatus.VERIFICATION_FAILED, result.model_dump())
            return result

        # 4. Status: EXECUTING
        exec_res = self.sandbox.execute(code, selected_artifacts)

        # Check for Execution Failure
        if not exec_res.get("success", False):
            v_res = VerificationResult(
                executed=CheckStatus.PASS,
                execution_success=CheckStatus.FAIL,
                output_present=CheckStatus.FAIL,
                output_valid=CheckStatus.FAIL,
                reproducible=CheckStatus.NOT_APPLICABLE,
                status="VERIFICATION_FAILED",
                confidence_score=0.0,
                errors=[exec_res.get("error", "Process execution failed.")]
            )
            result = AnalysisResult(
                analysis_id=analysis_id,
                question=request.question,
                answer=f"Execution failed: {exec_res.get('error', 'Execution error')}",
                status=AnalysisStatus.EXECUTION_FAILED,
                code=code,
                execution_result=exec_res,
                verification=v_res,
                confidence=0.0,
                error_message=exec_res.get("error")
            )
            storage_service.save_analysis_run(analysis_id, request.question, AnalysisStatus.EXECUTION_FAILED, result.model_dump())
            return result

        # 5. Status: VERIFYING
        out_present, out_valid, type_matched, result_errors = ResultChecker.check_result(exec_res, expected_type)

        repro_status, repro_diff, repro_method, repro_errors = ReproducibilityVerifier.verify_reproducibility(
            self.sandbox, code, exec_res, selected_artifacts
        )

        # Check dataset isolation / usage
        ds_used_status = CheckStatus.PASS if len(selected_artifacts) > 0 else CheckStatus.NOT_APPLICABLE

        # Data Quality verification check
        qual_performed = True
        qual_issues = len(quality_warnings) > 0
        crit_qual_issues = any(w.get("severity") == "critical" for w in quality_warnings)

        ver_passed = (
            exec_res.get("success", False) and
            out_present == CheckStatus.PASS and
            out_valid == CheckStatus.PASS and
            type_matched == CheckStatus.PASS and
            repro_status == CheckStatus.PASS
        )

        ver_status_str = "VERIFIED" if ver_passed else "VERIFICATION_FAILED"
        final_analysis_status = AnalysisStatus.VERIFIED if ver_passed else AnalysisStatus.VERIFICATION_FAILED

        v_result = VerificationResult(
            executed=CheckStatus.PASS,
            execution_success=CheckStatus.PASS if exec_res.get("success") else CheckStatus.FAIL,
            output_present=out_present,
            output_valid=out_valid,
            expected_type_matched=type_matched,
            reproducible=repro_status,
            selected_datasets_used=ds_used_status,
            result_consistent=CheckStatus.PASS if ver_passed else CheckStatus.FAIL,
            quality_check_performed=qual_performed,
            quality_issues_found=qual_issues,
            critical_quality_issues=crit_qual_issues,
            status=ver_status_str,
            comparison_method=repro_method,
            numeric_tolerance_difference=repro_diff,
            errors=result_errors + repro_errors
        )

        # Calculate confidence score
        flat_quality_warnings = [w for art in selected_artifacts for w in art.profile.quality_warnings]
        conf_score = ConfidenceCalculator.calculate_confidence(v_result, flat_quality_warnings)
        v_result.confidence_score = conf_score

        # Canonical output extraction
        parsed = exec_res.get("parsed_output", {})
        canonical_res = None
        if isinstance(parsed, dict) and "result" in parsed:
            canonical_res = CanonicalResult(
                result=parsed["result"],
                metric=parsed.get("metric", "value"),
                unit=parsed.get("unit"),
                dataset_ids=request.selected_datasets
            )

        # Build evidence collection
        evidence_coll = EvidenceAccumulator.build_evidence(
            request.selected_datasets,
            code,
            exec_res,
            doc_chunks=doc_chunks
        )

        # Synthesize final answer matching canonical result
        answer = self.analyst.synthesize_answer(request.question, exec_res, evidence_coll.items)

        result = AnalysisResult(
            analysis_id=analysis_id,
            question=request.question,
            answer=answer,
            status=final_analysis_status,
            code=code,
            expected_result_type=expected_type,
            execution_result=exec_res,
            canonical_result=canonical_res,
            evidence=evidence_coll.items,
            verification=v_result,
            confidence=conf_score
        )

        storage_service.save_analysis_run(analysis_id, request.question, final_analysis_status.value, result.model_dump())
        return result
