from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List
from ..core.translator_service import translate_to_multiple, TranslationError
from ..core.openai_service import analyze_translations, OpenAIError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class AutoTranslationRequest(BaseModel):
    text: str
    target_langs: List[str] = Field(
        default=["EN", "DE", "FR", "JA"],
        description="List of target language codes"
    )
    analyze: bool = Field(
        default=False,
        description="Whether to analyze translations using OpenAI"
    )

class AutoTranslationResponse(BaseModel):
    translations: Dict[str, str]
    detected_source_lang: str
    analysis: str | None = None

@router.post("/translate/auto", response_model=AutoTranslationResponse)
async def translate_auto(request: AutoTranslationRequest):
    """
    Auto-detect source language and translate to multiple target languages
    """
    try:
        translations = await translate_to_multiple(
            text=request.text,
            target_langs=request.target_langs
        )
        
        detected_lang = translations.pop("detected_source_lang")
        
        # 如果请求分析，调用 OpenAI API
        analysis = None
        if request.analyze:
            try:
                analysis = await analyze_translations(
                    translations=translations,
                    original_text=request.text
                )
            except OpenAIError as e:
                logger.error(f"OpenAI analysis failed: {str(e)}")
                # 即使分析失败，也返回翻译结果
        
        return AutoTranslationResponse(
            translations=translations,
            detected_source_lang=detected_lang,
            analysis=analysis
        )
    except TranslationError as e:
        raise HTTPException(status_code=400, detail=str(e))