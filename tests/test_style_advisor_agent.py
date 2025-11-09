import pytest
from unittest.mock import Mock, patch
from src.agents.style_advisor_agent import StyleAdvisorAgent
from src.core.mcp import MCPMessage

@pytest.fixture
def style_advisor_agent():
    return StyleAdvisorAgent()

@pytest.mark.asyncio
async def test_style_advisor_initialization(style_advisor_agent):
    assert style_advisor_agent is not None

@pytest.mark.asyncio
async def test_generate_recommendations(style_advisor_agent):
    test_message = {
        "customer_id": "CUST123",
        "context": {
            "occasion": "business",
            "season": "winter"
        }
    }
    
    with patch('src.agents.style_advisor_agent.StyleAdvisorAgent._analyze_customer_preferences') as mock_preferences:
        mock_preferences.return_value = {
            "preferred_colors": ["blue", "green"],
            "preferred_patterns": ["floral"],
            "style_profile": "casual-elegant",
            "price_range": "medium"
        }
        
        result = await style_advisor_agent.process(
            MCPMessage(
                message_type="style_advice_request",
                content=test_message
            )
        )
        
        assert result.message_type == "style_recommendations"
        assert "personal_style" in result.content
        assert "suggested_combinations" in result.content
        assert "seasonal_recommendations" in result.content
        
@pytest.mark.asyncio
async def test_missing_customer_id(style_advisor_agent):
    test_message = {
        "context": {
            "occasion": "business"
        }
    }
    
    result = await style_advisor_agent.process(
        MCPMessage(
            message_type="style_advice_request",
            content=test_message
        )
    )
    
    assert result.message_type == "error"
    assert "error" in result.content

@pytest.mark.asyncio
async def test_style_clustering(style_advisor_agent):
    with patch('src.agents.style_advisor_agent.StyleAdvisorAgent._extract_style_features') as mock_features:
        mock_features.return_value = [0.5, 0.3, 0.8]
        
        await style_advisor_agent._initialize_style_clusters()
        
        assert style_advisor_agent.style_clusters is not None