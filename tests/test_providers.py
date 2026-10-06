from backend.providers.mock import MockLLMProvider, MockEmbeddingProvider, MockCodeGenerationProvider

def test_mock_llm_provider():
    provider = MockLLMProvider()
    res = provider.generate("Test prompt")
    assert "[MOCK LLM GENERATION" in res

    plan = provider.plan_query("What is the total revenue?", [], [])
    assert plan["query_type"] == "data_aggregation"

def test_mock_embedding_provider():
    provider = MockEmbeddingProvider(dimension=64)
    emb = provider.embed_text("Sample text")
    assert len(emb) == 64

def test_mock_code_gen_provider():
    provider = MockCodeGenerationProvider()
    res = provider.generate_code("Calculate total revenue", [{"filename": "sales.csv"}], [])
    assert "code" in res
    assert "pd.read_csv" in res["code"]
