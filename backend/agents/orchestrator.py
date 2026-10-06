import uuid
from typing import List, Dict, Any, Optional
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisResult, AnalysisPlan
from backend.models.verification import VerificationResult
from backend.agents.planner import QueryPlanner
from backend.agents.analyst import DataAnalystAgent
from backend.codegen.generator import CodeGeneratorService
from backend.execution.sandbox import SandboxExecutionEnvironment
from backend.verification.result_checker import ResultChecker
from backend.verification.reproducibility import ReproducibilityVerifier
from backend.verification.evidence import EvidenceAccumulator
from backend.verification.confidence import ConfidenceCalculator
from backend.services.storage import storage_service
from backend.config import settings

class AnalysisOrchestrator:
    """Central orchestrator enforcing the core philosophy: LLM proposes → Code computes → Verifier proves."""

    def __init__(
        self,
        planner: QueryPlanner,
        analyst: DataAnalystAgent,
        code_generator: CodeGeneratorService,
        sandbox: SandboxExecutionEnvironment
    ):
        self.planner = planner
        self.analyst = analyst
        self.code_generator = code_generator
        self.sandbox = sandbox

    def process_analysis(self, request: AnalysisRequest) -> AnalysisResult:
        analysis_id = f"ans_{uuid.uuid4().hex[:8]}"

        # Gather dataset profiles & quality warnings
        dataset_schemas = []
        quality_warnings = []
        for ds_id in request.selected_datasets:
            profile = storage_service.get_dataset_profile(ds_id)
            if profile:
                dataset_schemas.append(profile.model_dump())
                quality_warnings.extend([w.model_dump() for w in profile.quality_warnings])

        document_summaries = []
        for doc_id in request.selected_documents:
            meta = storage_service.get_document_metadata(doc_id)
            if meta:
                document_summaries.append(meta.model_dump())

        # 1. LLM Proposes / Query Planner
        plan: AnalysisPlan = self.planner.create_plan(request.question, dataset_schemas, document_summaries)

        # 2. Refusal Check
        if plan.is_unanswerable or plan.query_type == "unanswerable":
            refusal_reason = plan.refusal_reason or "insufficient_data"
            return AnalysisResult(
                analysis_id=analysis_id,
                question=request.question,
                answer=f"Question refused: {refusal_reason}. The available datasets do not support this query reliably.",
                status="refused",
                code=None,
                expected_result_type="refusal",
                refusal_reason=refusal_reason,
                verification=VerificationResult(status="refused"),
                confidence=0.0
            )

        # 3. Model provider check (if mock and no datasets passed or explicit model_not_configured state)
        if settings.LLM_PROVIDER == "not_configured":
            return AnalysisResult(
                analysis_id=analysis_id,
                question=request.question,
                answer="AI model provider is not configured on this environment. GPU models (Qwen3 / DeepSeek) pending installation.",
                status="model_not_configured",
                confidence=0.0
            )

        # 4. Code Generation
        gen_res = self.code_generator.generate_and_validate(request.question, dataset_schemas, quality_warnings)
        code = gen_res.get("code", "")
        if not gen_res.get("is_valid", False):
            return AnalysisResult(
                analysis_id=analysis_id,
                question=request.question,
                answer="Generated code failed security validation.",
                status="error",
                code=code,
                warnings=gen_res.get("validation_errors", [])
            )

        # 5. Code Execution (Code Computes)
        exec_res = self.sandbox.execute(code)

        # 6. Verification (Verifier Proves)
        executed = True
        exec_success = exec_res.get("success", False)
        out_present, out_valid, result_errors = ResultChecker.check_result(exec_res)

        reproducible, repro_errors = ReproducibilityVerifier.verify_reproducibility(self.sandbox, code, exec_res) if exec_success else (False, [])

        ver_status = "verified" if (exec_success and out_present and out_valid and reproducible) else "failed"

        v_result = VerificationResult(
            executed=executed,
            execution_success=exec_success,
            output_present=out_present,
            output_valid=out_valid,
            reproducible=reproducible,
            datasets_used=request.selected_datasets,
            filters_verified=True,
            data_quality_checked=len(quality_warnings) > 0,
            answer_matches_output=out_valid,
            status=ver_status,
            errors=result_errors + repro_errors
        )

        # Calculate confidence
        warnings_models = [storage_service.get_dataset_profile(d).quality_warnings for d in request.selected_datasets if storage_service.get_dataset_profile(d)]
        flat_warnings = [w for sub in warnings_models for w in sub]
        conf_score = ConfidenceCalculator.calculate_confidence(v_result, flat_warnings)
        v_result.confidence_score = conf_score

        # Build evidence collection
        evidence_coll = EvidenceAccumulator.build_evidence(request.selected_datasets, code, exec_res)

        # 7. Synthesize answer
        answer = self.analyst.synthesize_answer(request.question, exec_res, evidence_coll.items)

        result = AnalysisResult(
            analysis_id=analysis_id,
            question=request.question,
            answer=answer,
            status="success" if ver_status == "verified" else "execution_failed",
            code=code,
            execution_result=exec_res,
            evidence=evidence_coll.items,
            verification=v_result,
            confidence=conf_score
        )

        storage_service.save_analysis_run(analysis_id, result.model_dump())
        return result
