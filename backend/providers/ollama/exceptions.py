class OllamaProviderError(Exception):
    """Base exception for Ollama provider errors."""
    pass

class OllamaUnavailableError(OllamaProviderError):
    """Raised when Ollama binary or local API service is unreachable."""
    pass

class ModelNotFoundError(OllamaProviderError):
    """Raised when the requested model is not installed in Ollama."""
    pass

class OllamaTimeoutError(OllamaProviderError):
    """Raised when Ollama inference times out."""
    pass

class OllamaResponseError(OllamaProviderError):
    """Raised when Ollama returns an unexpected HTTP error or invalid response format."""
    pass

class StructuredOutputValidationError(OllamaProviderError):
    """Raised when Ollama output fails structured JSON schema validation."""
    pass
