from openai import OpenAI
from typing import Dict
from .config import settings
import logging

logger = logging.getLogger(__name__)

class OpenAIError(Exception):
    pass

async def analyze_translations(translations: Dict[str, str], original_text: str) -> str:
    """
    Analyze all translations together using OpenAI GPT-4o-mini
    """
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt = f"""
        Original text: {original_text}
        
        Translations:
        {'\n'.join([f'{lang}: {text}' for lang, text in translations.items()])}
        
        Please analyze these translations and provide:
        1. Accuracy assessment
        2. Any significant differences between translations
        """
        
        logger.info("Sending request to OpenAI API for overall analysis")
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a multilingual translation expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        analysis = completion.choices[0].message.content
        logger.info("Received overall analysis from OpenAI")
        return analysis
        
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise OpenAIError(f"OpenAI API error: {str(e)}")

async def ask_gpt(
    text: str,
    translated_text: str,
    lang_code: str
) -> str:
    """
    Use translated text as a direct question to GPT
    """
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        logger.info(f"Sending {lang_code} translation as question to GPT")
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": translated_text}
            ]
        )
        
        response = completion.choices[0].message.content
        logger.info(f"Received response for {lang_code} question")
        return response
        
    except Exception as e:
        logger.error(f"OpenAI API error for {lang_code}: {str(e)}")
        raise OpenAIError(f"OpenAI API error for {lang_code}: {str(e)}")

async def ask_gpt_all(
    translations: Dict[str, str],
    original_text: str
) -> Dict[str, str]:
    """
    Send each translation as a separate question to GPT
    """
    responses = {}
    for lang, translated_text in translations.items():
        try:
            response = await ask_gpt(
                text=original_text,
                translated_text=translated_text,
                lang_code=lang
            )
            responses[lang] = response
        except OpenAIError as e:
            logger.error(f"Failed to get response for {lang} question: {str(e)}")
            responses[lang] = f"Failed to get response: {str(e)}"
    return responses