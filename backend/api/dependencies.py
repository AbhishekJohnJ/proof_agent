from backend.providers.factory import ProviderFactory
from backend.agents.planner import QueryPlanner
from backend.agents.analyst import DataAnalystAgent
from backend.agents.document_agent import DocumentAgent
from backend.codegen.generator import CodeGeneratorService
from backend.execution.sandbox import LocalIsolatedSandbox, DockerSandbox
from backend.rag.vector_store import global_vector_store
from backend.rag.embeddings import EmbeddingService
from backend.rag.retriever import DocumentRetriever
from backend.agents.orchestrator import AnalysisOrchestrator
from backend.config import settings

def get_orchestrator() -> AnalysisOrchestrator:
    llm = ProviderFactory.get_llm_provider()
    code_gen = ProviderFactory.get_code_gen_provider()
    embedding_provider = ProviderFactory.get_embedding_provider()

    planner = QueryPlanner(llm_provider=llm)
    analyst = DataAnalystAgent(llm_provider=llm)
    code_service = CodeGeneratorService(provider=code_gen)

    if settings.SANDBOX_ENABLED:
        sandbox = DockerSandbox()
    else:
        sandbox = LocalIsolatedSandbox()

    emb_service = EmbeddingService(embedding_provider)
    retriever = DocumentRetriever(global_vector_store, emb_service)
    doc_agent = DocumentAgent(retriever)

    return AnalysisOrchestrator(
        planner=planner,
        analyst=analyst,
        document_agent=doc_agent,
        code_generator=code_service,
        sandbox=sandbox
    )
