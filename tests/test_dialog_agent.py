import pytest
from unittest.mock import Mock, patch
from src.agents.dialog_agent import DialogAgent

@pytest.fixture
def dialog_agent():
    return DialogAgent()

@pytest.mark.asyncio
async def test_dialog_agent_initialization(dialog_agent):
    assert dialog_agent is not None

@pytest.mark.asyncio
async def test_process_message(dialog_agent):
    test_message = "Show me red silk scarves"
    
    with patch('src.agents.dialog_agent.DialogAgent._extract_intent') as mock_intent:
        mock_intent.return_value = {
            "intent": "search_product",
            "filters": {
                "color": "red",
                "material": "silk"
            }
        }
        
        result = await dialog_agent.process_message(test_message)
        
        assert result is not None
        assert "intent" in result
        assert result["intent"] == "search_product"
        assert "filters" in result
        
        mock_intent.assert_called_once_with(test_message)

@pytest.mark.asyncio
async def test_multilingual_support(dialog_agent):
    messages = {
        "fr": "Montrez-moi des foulards en soie rouge",
        "es": "Muéstrame bufandas de seda rojas",
        "en": "Show me red silk scarves"
    }
    
    for lang, msg in messages.items():
        with patch('src.agents.dialog_agent.DialogAgent._detect_language') as mock_lang:
            mock_lang.return_value = lang
            
            result = await dialog_agent.process_message(msg)
            assert result is not None
            
            mock_lang.assert_called_once_with(msg)

@pytest.mark.asyncio
async def test_context_management(dialog_agent):
    conversation_id = "test_conv_123"
    
    # First message
    msg1 = "Show me silk scarves"
    result1 = await dialog_agent.process_message(msg1, conversation_id=conversation_id)
    
    # Follow-up message
    msg2 = "Show me the red ones"
    result2 = await dialog_agent.process_message(msg2, conversation_id=conversation_id)
    
    assert result2["context"]["previous_filters"] == result1["filters"]
