import pytest
from unittest.mock import Mock, patch
from src.agents.transaction_agent import TransactionAgent

@pytest.fixture
def transaction_agent():
    return TransactionAgent()

@pytest.mark.asyncio
async def test_transaction_agent_initialization(transaction_agent):
    assert transaction_agent is not None

@pytest.mark.asyncio
async def test_create_order(transaction_agent):
    test_order = {
        "customer_id": "CUST123",
        "products": [
            {"id": "SCARF123", "quantity": 2},
            {"id": "SCARF456", "quantity": 1}
        ],
        "shipping_address": "123 Test St, City"
    }
    
    with patch('src.agents.transaction_agent.TransactionAgent._validate_order') as mock_validate:
        mock_validate.return_value = True
        
        with patch('src.agents.transaction_agent.TransactionAgent._process_payment') as mock_payment:
            mock_payment.return_value = {
                "success": True,
                "transaction_id": "TRX789"
            }
            
            result = await transaction_agent.create_order(test_order)
            
            assert result is not None
            assert result["success"] is True
            assert "order_id" in result
            assert "transaction_id" in result
            
            mock_validate.assert_called_once_with(test_order)
            mock_payment.assert_called_once()

@pytest.mark.asyncio
async def test_order_validation(transaction_agent):
    # Valid order
    valid_order = {
        "customer_id": "CUST123",
        "products": [{"id": "SCARF123", "quantity": 1}],
        "shipping_address": "123 Test St, City"
    }
    
    # Invalid orders
    invalid_orders = [
        {},  # Empty order
        {"customer_id": "CUST123"},  # Missing products
        {"customer_id": "CUST123", "products": []},  # Empty products
        {"products": [{"id": "SCARF123", "quantity": 1}]}  # Missing customer_id
    ]
    
    assert await transaction_agent.validate_order(valid_order) is True
    
    for invalid_order in invalid_orders:
        with pytest.raises(ValueError):
            await transaction_agent.validate_order(invalid_order)

@pytest.mark.asyncio
async def test_payment_processing(transaction_agent):
    test_payment = {
        "order_id": "ORDER123",
        "amount": 150.00,
        "currency": "USD",
        "payment_method": {
            "type": "credit_card",
            "token": "tok_test123"
        }
    }
    
    with patch('src.agents.transaction_agent.TransactionAgent._process_payment') as mock_payment:
        # Successful payment
        mock_payment.return_value = {
            "success": True,
            "transaction_id": "TRX789"
        }
        
        result = await transaction_agent.process_payment(test_payment)
        assert result["success"] is True
        assert "transaction_id" in result
        
        # Failed payment
        mock_payment.return_value = {
            "success": False,
            "error": "Payment declined"
        }
        
        result = await transaction_agent.process_payment(test_payment)
        assert result["success"] is False
        assert "error" in result