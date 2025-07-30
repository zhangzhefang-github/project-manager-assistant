from langchain_openai import AzureChatOpenAI, ChatOpenAI
from app.core.config import settings

def get_llm():
    """Factory function to get the configured LLM instance."""
    if settings.MODEL_PROVIDER == 'Azure':
        return AzureChatOpenAI(
            api_key=settings.AZURE_OPEN_AI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_version=settings.OPENAI_API_VERSION,
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        )
    elif settings.MODEL_PROVIDER == 'OpenAI':
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            organization=None  # Explicitly set to None to avoid potential conflicts
        )
    else:
        raise ValueError(f"Unsupported model provider: {settings.MODEL_PROVIDER}")

# Global LLM instance
llm = get_llm() 