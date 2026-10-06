from backend.providers.mock import MockLLMProvider, MockEmbeddingProvider, MockCodeGenerationProvider
from backend.agents.planner import QueryPlanner
from backend.agents.analyst import DataAnalystAgent
from backend.codegen.generator import CodeGeneratorService
from backend.execution.sandbox import LocalIsolatedSandbox
from backend.agents.orchestrator import AnalysisOrchestrator

def get_orchestrator() -> AnalysisOrchestrator:
    llm = MockLLMProvider()
    code_gen = MockCodeGenerationProvider()
    
    planner = QueryPlanner(llm_provider=llm)
    analyst = DataAnalystAgent(llm_provider=llm)
    code_service = CodeGeneratorService(provider=code_gen)
    sandbox = LocalIsolatedSandbox()

    return AnalysisOrchestrator(
        planner=planner,
        analyst=analyst,
        code_generator=code_service,
        sandbox=sandbox
    )
