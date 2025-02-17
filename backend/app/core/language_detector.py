import requests
from typing import Optional
from .config import settings
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageDetectionError(Exception):
    pass

async def detect_language(text: str) -> str:
    """
    Detect the language of input text using DeepL API
    """
    # 添加 API key 验证
    if not settings.DEEPL_API_KEY:
        logger.error("DeepL API key is not set")
        raise LanguageDetectionError("DeepL API key is not configured")
        
    try:
        payload = {
            "text": text,
            "target_lang": "EN",  # 使用任意目标语言
            "auth_key": settings.DEEPL_API_KEY,
        }
        
        logger.info(f"Detecting language for text: {text}")
        logger.info(f"Using API URL: {settings.DEEPL_API_URL}")
        logger.info(f"API Key (first 4 chars): {settings.DEEPL_API_KEY[:4]}...")
        
        response = requests.post(
            settings.DEEPL_API_URL,  # 使用翻译 API 端点
            data=payload
        )
        logger.info(f"DeepL API Response Status: {response.status_code}")
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"DeepL API Response: {result}")
        
        # DeepL API 会在翻译结果中返回检测到的源语言
        detected_lang = result["translations"][0]["detected_source_language"]
        logger.info(f"Detected language: {detected_lang}")
        return detected_lang
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Language detection failed: {str(e)}")
        raise LanguageDetectionError(f"Language detection failed: {str(e)}")
    except (KeyError, IndexError) as e:
        logger.error(f"Invalid response format: {str(e)}")
        raise LanguageDetectionError(f"Invalid response format: {str(e)}") 