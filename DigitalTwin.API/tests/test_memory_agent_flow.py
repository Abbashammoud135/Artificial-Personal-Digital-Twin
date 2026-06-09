import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.memory.agent import MemoryAgent


class MockLLMResponse:
    def __init__(self, content):
        self.content = content


@pytest.mark.asyncio
async def test_safe_parse_json_with_comments():
    """Verify that safe_parse_json handles single-line and multi-line comments."""
    agent = MemoryAgent()
    
    # Input JSON containing comments which would break typical json.loads
    json_with_comments = """
    {
      "collection": "medical_documents",
      "filter": {
        "user_id": "dummy", // inline comment here
        "analysis.risk_profile.abnormal_count": {
          "$gt": 0 /* block comment
          across multiple lines */
        }
      },
      "sort": null,
      "limit": 5
    }
    """
    
    parsed = agent.safe_parse_json(json_with_comments)
    assert parsed["collection"] == "medical_documents"
    assert parsed["filter"]["user_id"] == "dummy"
    assert parsed["filter"]["analysis.risk_profile.abnormal_count"]["$gt"] == 0
    assert parsed["limit"] == 5


@pytest.mark.asyncio
async def test_query_memory_flow():
    """Test the complete query memory execution flow with mocks."""
    agent = MemoryAgent()

    # Mock LLM and Repository
    agent.llm = MagicMock()
    agent.repo = MagicMock()
    agent.repo.search = AsyncMock(return_value=[
        {"_id": "doc1", "analysis": {"risk_profile": {"overall": 0.8}}}
    ])
    agent.repo.save_memory = AsyncMock(return_value={"status": "success"})

    # Setup LLM mock replies
    # First invoke (for generate_query)
    mock_query_reply = MockLLMResponse("""
    {
      "collection": "medical_documents",
      "filter": {
        "analysis.risk_profile.abnormal_count": { "$gt": 0 } // abnormal count comment
      },
      "sort": null,
      "limit": null
    }
    """)
    # Second invoke (for generate_answer_from_results)
    mock_answer_reply = MockLLMResponse("The patient has high cardiovascular risk scores of 0.8.")

    agent.llm.invoke.side_effect = [mock_query_reply, mock_answer_reply]

    user_id = "test_user_99"
    user_request = "show me abnormal lab results"

    result = await agent.query_memory(user_request, user_id=user_id)

    # 1. Verify that user_id was programmatically injected into the filter
    query_used = result["query"]
    assert query_used["filter"]["user_id"] == user_id
    assert query_used["filter"]["analysis.risk_profile.abnormal_count"]["$gt"] == 0

    # 2. Verify search was called with the injected query
    agent.repo.search.assert_called_once_with(query_used)

    # 3. Verify answer is generated and correct
    assert result["answer"] == "The patient has high cardiovascular risk scores of 0.8."

    # 4. Verify memory saving is called
    agent.repo.save_memory.assert_called_once()
    saved_args = agent.repo.save_memory.call_args[0]
    assert saved_args[0] == user_id
    assert saved_args[1]["query"] == user_request
    assert saved_args[1]["extracted_answer"] == result["answer"]
    assert saved_args[1]["result_count"] == 1


if __name__ == "__main__":
    # Allow running the test directly
    asyncio.run(test_safe_parse_json_with_comments())
    asyncio.run(test_query_memory_flow())
    print("✓ All mock unit tests passed successfully!")
