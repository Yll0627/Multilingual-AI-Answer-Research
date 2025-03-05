import requests
from typing import Dict, List, Optional
from .config import settings
from .language_detector import detect_language, LanguageDetectionError
import logging

# 设置日志
logger = logging.getLogger(__name__)

class TranslationError(Exception):
    pass

async def translate_to_multiple(
    text: str,
    target_langs: List[str] = ["EN-US", "AR", "ZH", "ES"]
) -> Dict[str, str]:
    """
    Auto-detect source language and translate text to multiple target languages
    EN-US: English (American)
    AR: Arabic
    ZH: Chinese
    ES: Spanish
    """
    # 添加 API key 验证
    if not settings.DEEPL_API_KEY:
        logger.error("DeepL API key is not set")
        raise TranslationError("DeepL API key is not configured")
        
    translations = {}
    try:
        logger.info(f"Starting translation for text: {text}")
        # 自动检测源语言
        source_lang = await detect_language(text)
        logger.info(f"Detected source language: {source_lang}")
        
        for target_lang in target_langs:
            logger.info(f"Translating to {target_lang}")
            # 跳过与源语言相同的目标语言
            if target_lang.upper() == source_lang.upper():
                translations[target_lang] = text
                logger.info(f"Skipped translation to {target_lang} (same as source)")
                continue
                
            payload = {
                "text": text,
                "target_lang": target_lang.upper(),
                "auth_key": settings.DEEPL_API_KEY,
            }

            logger.info(f"Sending request to DeepL API for {target_lang}")
            response = requests.post(settings.DEEPL_API_URL, data=payload)
            logger.info(f"DeepL API Response Status: {response.status_code}")
            response.raise_for_status()
            
            result = response.json()
            translations[target_lang] = result["translations"][0]["text"]
            logger.info(f"Translation to {target_lang} completed")
        
        # 添加检测到的源语言信息
        translations["detected_source_lang"] = source_lang
        logger.info("Translation process completed successfully")
        return translations
        
    except LanguageDetectionError as e:
        logger.error(f"Language detection failed: {str(e)}")
        raise TranslationError(f"Language detection failed: {str(e)}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Translation request failed: {str(e)}")
        raise TranslationError(f"Translation request failed: {str(e)}")
    except (KeyError, IndexError) as e:
        logger.error(f"Invalid response format: {str(e)}")
        raise TranslationError(f"Invalid response format: {str(e)}")

# 保留原来的单语言翻译函数以保持向后兼容
async def translate_text(
    text: str,
    target_lang: str,
    source_lang: Optional[str] = None
) -> str:
    translations = await translate_to_multiple(text, [target_lang])
    return translations[target_lang]

async def translate_responses_to_english(responses: Dict[str, str]) -> Dict[str, str]:
    """
    Translate all responses to English except those already in English
    """
    english_responses = {}
    try:
        for lang, response in responses.items():
            if lang != "EN":  # Skip if already English
                translations = await translate_to_multiple(
                    text=response,
                    target_langs=["EN"]
                )
                english_responses[lang] = translations["EN"]
            else:
                english_responses[lang] = response
                
        return english_responses
        
    except Exception as e:
        logger.error(f"Failed to translate responses to English: {str(e)}")
        raise TranslationError(f"Failed to translate responses to English: {str(e)}")
