import pytest
from unittest.mock import Mock, patch
from src.agents.inventory_agent import InventoryAgent

@pytest.fixture
def inventory_agent():
    return InventoryAgent()

@pytest.mark.asyncio
async def test_inventory_agent_initialization(inventory_agent):
    assert inventory_agent is not None

@pytest.mark.asyncio
async def test_check_availability(inventory_agent):
    test_product_id = "SCARF123"
    
    with patch('src.agents.inventory_agent.InventoryAgent._query_database') as mock_query:
        mock_query.return_value = {
            "product_id": test_product_id,
            "quantity": 5,
            "status": "in_stock"
        }
        
        result = await inventory_agent.check_availability(test_product_id)
        
        assert result is not None
        assert result["product_id"] == test_product_id
        assert result["quantity"] > 0
        assert result["status"] == "in_stock"
        
        mock_query.assert_called_once_with(test_product_id)

@pytest.mark.asyncio
async def test_reserve_product(inventory_agent):
    test_product_id = "SCARF123"
    test_quantity = 2
    
    with patch('src.agents.inventory_agent.InventoryAgent._update_stock') as mock_update:
        mock_update.return_value = {
            "success": True,
            "remaining_quantity": 3
        }
        
        result = await inventory_agent.reserve_product(test_product_id, test_quantity)
        
        assert result["success"] is True
        assert result["remaining_quantity"] >= 0
        
        mock_update.assert_called_once_with(test_product_id, test_quantity)

@pytest.mark.asyncio
async def test_stock_alerts(inventory_agent):
    test_threshold = 5
    
    with patch('src.agents.inventory_agent.InventoryAgent._check_low_stock') as mock_check:
        mock_check.return_value = [
            {"product_id": "SCARF123", "quantity": 3},
            {"product_id": "SCARF456", "quantity": 2}
        ]
        
        alerts = await inventory_agent.get_low_stock_alerts(threshold=test_threshold)
        
        assert len(alerts) > 0
        assert all(item["quantity"] < test_threshold for item in alerts)
        
        mock_check.assert_called_once_with(test_threshold)