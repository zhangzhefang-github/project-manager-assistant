import pytest
from langchain_core.messages import AIMessage

from app.services.llm_service import llm


@pytest.mark.integration
@pytest.mark.xfail(reason="This test makes a real API call and requires a valid API key with sufficient quota.")
def test_llm_service_integration():
    """
    Integration test to verify the LLM service is configured and working correctly.
    This test makes a real call to the configured LLM API.
    """
    # Act
    response = llm.invoke("讲个笑话")

    # Assert
    assert response is not None
    assert isinstance(response, AIMessage)
    assert response.content is not None
    assert len(response.content) > 0

    print(f"\nLLM Response: {response.content}") 