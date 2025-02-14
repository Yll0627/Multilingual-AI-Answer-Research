from openai import OpenAI
from typing import Dict
from .config import settings
import logging

logger = logging.getLogger(__name__)

class OpenAIError(Exception):
    pass

async def analyze_translations(translations: Dict[str, str], original_text: str) -> str:
    """
    Analyze translations using OpenAI GPT-4
    """
    try:
        # 创建 OpenAI 客户端
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # 构建提示信息
        prompt = f"""
        Original text: {original_text}
        
        Translations:
        {'\n'.join([f'{lang}: {text}' for lang, text in translations.items()])}
        
        Please analyze these translations and provide:
        1. Accuracy assessment
        2. Cultural nuances
        3. Any significant differences between translations
        4. Suggestions for improvement
        """
        
        logger.info("Sending request to OpenAI API")
        
        # 使用新的 API 调用方式，移除了 store 参数
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a multilingual translation expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 获取分析结果
        analysis = completion.choices[0].message.content
        logger.info("Received analysis from OpenAI")
        return analysis
        
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise OpenAIError(f"OpenAI API error: {str(e)}")