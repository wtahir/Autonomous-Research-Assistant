import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Initialize client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01"
)

# 3. Test connection
try:
    print("Testing Azure OpenAI connection...")
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),  # Your deployment name
        messages=[{"role": "user", "content": "Say 'Hello world' in Spanish"}],
        temperature=0
    )
    
    print("\nSuccess! Response:")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"\nFailed: {type(e).__name__}: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Verify .env variables match your Azure portal")
    print("2. Check deployment is running in Azure Studio")
    print("3. Test API key manually with curl (see comments)")