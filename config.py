import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AzureConfig:
    """Central configuration for Azure OpenAI"""
    API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-06")  # Default to latest stable version
    CHAT_DEPLOYMENT = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o")  # Your chat deployment name
    EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")  # Your embeddings deployment name

    @classmethod
    def validate(cls):
        """Validate all required credentials are present"""
        required_vars = {
            'API_KEY': cls.API_KEY,
            'ENDPOINT': cls.ENDPOINT,
            'CHAT_DEPLOYMENT': cls.CHAT_DEPLOYMENT
        }
        missing = [name for name, value in required_vars.items() if not value]
        if missing:
            raise ValueError(f"Missing required Azure config variables: {', '.join(missing)}")