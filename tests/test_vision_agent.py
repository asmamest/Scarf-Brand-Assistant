import pytest
from unittest.mock import Mock, patch
from src.agents.vision_agent import VisionAgent

def test_vision_agent_initialization():
    agent = VisionAgent()
    assert agent is not None

@pytest.mark.asyncio
async def test_process_image():
    agent = VisionAgent()
    test_image_url = "https://example.com/test-scarf.jpg"
    
    with patch('src.agents.vision_agent.VisionAgent._download_image') as mock_download:
        mock_download.return_value = b"fake_image_data"
        
        with patch('src.agents.vision_agent.VisionAgent._analyze_image') as mock_analyze:
            mock_analyze.return_value = {
                "colors": ["red", "blue"],
                "patterns": ["floral"],
                "style": "casual"
            }
            
            result = await agent.process_image(test_image_url)
            
            assert result is not None
            assert "colors" in result
            assert "patterns" in result
            assert "style" in result
            
            mock_download.assert_called_once_with(test_image_url)
            mock_analyze.assert_called_once_with(b"fake_image_data")

@pytest.mark.asyncio
async def test_error_handling():
    agent = VisionAgent()
    
    with pytest.raises(ValueError):
        await agent.process_image("")
        
    with pytest.raises(Exception):
        await agent.process_image("invalid_url")
