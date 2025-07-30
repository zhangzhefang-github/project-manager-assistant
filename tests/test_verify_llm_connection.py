import pytest
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from app.core.config import settings

@pytest.mark.llm_verification
def test_openai_api_base_connection():
    """
    Verifies that the configured OPENAI_API_BASE is reachable and the API key is valid.
    
    This test makes a real, simple, and cheap network request to the configured LLM service.
    It directly uses the settings from the .env file.
    
    How to run this specific test:
    $ uv run pytest -m llm_verification
    """
    assert settings.OPENAI_API_KEY, "OPENAI_API_KEY must be set in your .env file."
    assert settings.OPENAI_API_BASE, "OPENAI_API_BASE must be set in your .env file."

    # --- FINAL DIAGNOSTIC STEP ---
    # Print the key that the application is actually seeing at runtime.
    # This will definitively tell us if the .env file is being loaded correctly
    # or if a global environment variable is still overriding it.
    key = settings.OPENAI_API_KEY
    print(f"\n[DIAGNOSTIC] Using API Key starting with '{key[:8]}' and ending with '{key[-4:]}'")
    # --- END OF DIAGNOSTIC STEP ---

    try:
        # Initialize the ChatOpenAI client with settings from the .env file
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            organization=None,
            temperature=0
        )

        # Make a simple, low-cost API call
        response = llm.invoke("Say hi")

        # Assert that we received a valid response
        assert isinstance(response, AIMessage), "Response should be an AIMessage instance."
        assert response.content, "Response content should not be empty."
        
        print(f"\n✅ LLM Connection Successful!")
        print(f"   - API Base: {settings.OPENAI_API_BASE}")
        print(f"   - Response: {response.content}")

    except Exception as e:
        pytest.fail(
            f"\n❌ LLM Connection Failed.\n"
            f"   - API Base: {settings.OPENAI_API_BASE}\n"
            f"   - Error: {e}\n"
            f"   - Please check your .env file and ensure the API key has sufficient quota."
        ) 