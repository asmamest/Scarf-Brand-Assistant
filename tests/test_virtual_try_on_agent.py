import pytest
from unittest.mock import Mock, patch
from src.agents.virtual_try_on_agent import VirtualTryOnAgent

@pytest.fixture
def virtual_try_on_agent():
    return VirtualTryOnAgent()

@pytest.mark.asyncio
async def test_virtual_try_on_agent_initialization(virtual_try_on_agent):
    assert virtual_try_on_agent is not None

@pytest.mark.asyncio
async def test_process_try_on(virtual_try_on_agent):
    test_message = {
        "scarf_image": "test_scarf.jpg",
        "user_photo": "test_user.jpg"
    }
    
    with patch('src.agents.virtual_try_on_agent.VirtualTryOnAgent._generate_try_on') as mock_try_on:
        mock_try_on.return_value = {
            "image_url": "result.jpg",
            "lighting": {"natural": 0.8},
            "fit_score": 0.85,
            "recommendations": ["Test recommendation"]
        }
        
        result = await virtual_try_on_agent.process(
            MCPMessage(
                message_type="virtual_try_on_request",
                content=test_message
            )
        )
        
        assert result.message_type == "virtual_try_on_result"
        assert "result_image" in result.content
        assert "lighting_conditions" in result.content
        assert "fit_score" in result.content
        
@pytest.mark.asyncio
async def test_missing_images(virtual_try_on_agent):
    test_cases = [
        {"scarf_image": "test.jpg"},  # Missing user photo
        {"user_photo": "test.jpg"},   # Missing scarf image
        {}                            # Missing both
    ]
    
    for test_case in test_cases:
        result = await virtual_try_on_agent.process(
            MCPMessage(
                message_type="virtual_try_on_request",
                content=test_case
            )
        )
        
        assert result.message_type == "error"
        assert "error" in result.content