import pytest
from fastapi.testclient import TestClient
from app.core.translator_service import translate_text
from main import app

client = TestClient(app)

def test_translate_endpoint():
    response = client.post(
        "/api/translate",
        json={
            "text": "Hello world",
            "target_lang": "DE"
        }
    )
    assert response.status_code == 200
    assert "translated_text" in response.json()

@pytest.mark.asyncio
async def test_translate_text():
    text = "Hello world"
    target_lang = "DE"
    
    result = await translate_text(text=text, target_lang=target_lang)
    assert isinstance(result, str)
    assert len(result) > 0 