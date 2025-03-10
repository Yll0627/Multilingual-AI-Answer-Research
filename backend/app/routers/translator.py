from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from ..core.translator_service import (
    translate_to_multiple, 
    translate_responses_to_english,
    TranslationError
)
# from ..core.openai_service import analyze_translations  # 暂时不使用翻译分析功能
from ..core.openai_service import ask_gpt_all, ask_gpt, OpenAIError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class AutoTranslationRequest(BaseModel):
    text: str
    target_langs: List[str] = Field(
        default=["EN-US", "AR", "ZH", "ES"],
        description="List of target language codes: EN-US (American English), AR (Arabic), ZH (Chinese), ES (Spanish)"
    )
    single_language: Optional[str] = Field(
        default=None,
        description="Single language code for translation and response"
    )
    question_response: bool = Field(
        default=False,
        description="Whether to get responses for each translation as questions"
    )

class AutoTranslationResponse(BaseModel):
    translations: Dict[str, str]
    detected_source_lang: str
    question_responses: Dict[str, str] | None = None
    english_responses: Dict[str, str] | None = None

@router.post("/translate/auto", response_model=AutoTranslationResponse)
async def translate_auto(request: AutoTranslationRequest):
    """
    Auto-detect source language and translate to multiple target languages
    """
    try:
        # 如果指定了单一语言，则只翻译该语言
        target_langs = [request.single_language] if request.single_language else request.target_langs
        
        translations = await translate_to_multiple(
            text=request.text,
            target_langs=target_langs
        )
        
        detected_lang = translations.pop("detected_source_lang")
        
        question_responses = None
        english_responses = None
        
        if request.question_response:
            try:
                if request.single_language:
                    # 单语言模式：只获取一种语言的回答
                    single_response = await ask_gpt(
                        text=request.text,
                        translated_text=translations[request.single_language],
                        lang_code=request.single_language
                    )
                    question_responses = {request.single_language: single_response}
                    
                    # 如果不是英语，则翻译成英语
                    if request.single_language != "EN-US":
                        english_translation = await translate_to_multiple(
                            text=single_response,
                            target_langs=["EN-US"]
                        )
                        english_responses = {request.single_language: english_translation["EN-US"]}
                else:
                    # 多语言模式：获取所有语言的回答
                    question_responses = await ask_gpt_all(
                        translations=translations,
                        original_text=request.text
                    )
                    english_responses = await translate_responses_to_english(question_responses)
                        
            except OpenAIError as e:
                logger.error(f"Question responses failed: {str(e)}")
        
        return AutoTranslationResponse(
            translations=translations,
            detected_source_lang=detected_lang,
            question_responses=question_responses,
            english_responses=english_responses
        )
    except TranslationError as e:
        raise HTTPException(status_code=400, detail=str(e))