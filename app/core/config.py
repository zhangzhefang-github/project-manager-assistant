from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    MODEL_PROVIDER: str = "OpenAI"

    # OpenAI Configuration
    OPENAI_API_KEY: str = "sk-..."
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    OPENAI_API_VERSION: str = "2024-05-01-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4o-mini"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

settings = Settings() 