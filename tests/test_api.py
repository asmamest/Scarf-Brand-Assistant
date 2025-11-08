import pytest
from fastapi.testclient import TestClient
from src.main import app

def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_webhook_endpoint(test_client):
    # Test image message
    image_payload = {
        "message": {
            "type": "image",
            "image": {
                "url": "https://example.com/scarf.jpg"
            }
        },
        "customer": {
            "id": "123"
        }
    }
    
    response = test_client.post("/webhook/whatsapp", json=image_payload)
    assert response.status_code == 200
    
    # Test text message
    text_payload = {
        "message": {
            "type": "text",
            "text": "Show me red silk scarves"
        },
        "customer": {
            "id": "123"
        }
    }
    
    response = test_client.post("/webhook/whatsapp", json=text_payload)
    assert response.status_code == 200

def test_invalid_webhook_payload(test_client):
    invalid_payloads = [
        {},  # Empty payload
        {"message": {}},  # Empty message
        {"message": {"type": "unknown"}},  # Invalid message type
        {"message": {"type": "image"}},  # Missing image URL
    ]
    
    for payload in invalid_payloads:
        response = test_client.post("/webhook/whatsapp", json=payload)
        assert response.status_code == 400

def test_cors_headers(test_client):
    response = test_client.options("/webhook/whatsapp")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers