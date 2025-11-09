import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.agents.trend_analyzer_agent import TrendAnalyzerAgent
from src.core.mcp import MCPMessage

@pytest.fixture
def trend_analyzer_agent():
    return TrendAnalyzerAgent()

@pytest.mark.asyncio
async def test_trend_analyzer_initialization(trend_analyzer_agent):
    assert trend_analyzer_agent is not None

@pytest.mark.asyncio
async def test_get_current_trends(trend_analyzer_agent):
    with patch('src.agents.trend_analyzer_agent.TrendAnalyzerAgent._get_recent_interactions') as mock_interactions:
        mock_interactions.return_value = [
            {
                "type": "view",
                "content": "product_123",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        result = await trend_analyzer_agent.process(
            MCPMessage(
                message_type="trend_analysis_request",
                content={"action": "get_trends"}
            )
        )
        
        assert result.message_type == "trend_analysis"
        assert "popular_items" in result.content
        assert "color_trends" in result.content
        assert "style_trends" in result.content

@pytest.mark.asyncio
async def test_analyze_specific_trend(trend_analyzer_agent):
    test_message = {
        "action": "analyze_trend",
        "trend_type": "pattern",
        "trend_id": "geometric"
    }
    
    result = await trend_analyzer_agent.process(
        MCPMessage(
            message_type="trend_analysis_request",
            content=test_message
        )
    )
    
    assert result.message_type == "trend_analysis"
    
@pytest.mark.asyncio
async def test_predict_future_trends(trend_analyzer_agent):
    test_message = {
        "action": "predict_trends",
        "timeframe": "next_month"
    }
    
    with patch('src.agents.trend_analyzer_agent.TrendAnalyzerAgent._get_historical_data') as mock_history:
        mock_history.return_value = {
            "sales_history": [],
            "interaction_patterns": [],
            "seasonal_trends": []
        }
        
        result = await trend_analyzer_agent.process(
            MCPMessage(
                message_type="trend_analysis_request",
                content=test_message
            )
        )
        
        assert result.message_type == "trend_analysis"
        assert "predictions" in result.content
        assert "confidence_scores" in result.content

@pytest.mark.asyncio
async def test_trend_caching(trend_analyzer_agent):
    # Premier appel
    await trend_analyzer_agent.process(
        MCPMessage(
            message_type="trend_analysis_request",
            content={"action": "get_trends"}
        )
    )
    
    # Vérifier que les données sont en cache
    assert "current_trends" in trend_analyzer_agent.trends_cache
    
    # Vérifier que le cache expire correctement
    trend_analyzer_agent.trends_cache["current_trends"]["timestamp"] = (
        datetime.now() - timedelta(hours=2)
    )
    
    # Deuxième appel devrait régénérer le cache
    result = await trend_analyzer_agent.process(
        MCPMessage(
            message_type="trend_analysis_request",
            content={"action": "get_trends"}
        )
    )
    
    assert result.message_type == "trend_analysis"