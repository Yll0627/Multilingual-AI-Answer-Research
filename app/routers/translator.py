from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List
from ..core.translator_service import translate_to_multiple, TranslationError
from ..core.openai_service import analyze_translations, analyze_all_translations, OpenAIError
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
    individual_analysis: bool = Field(
        default=False,
        description="Whether to analyze each translation separately"
    )

class AutoTranslationResponse(BaseModel):
    translations: Dict[str, str]
    detected_source_lang: str
    analysis: str | None = None
    individual_analyses: Dict[str, str] | None = None

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
        
        analysis = None
        individual_analyses = None
        
        if request.analyze:
            try:
                analysis = await analyze_translations(
                    translations=translations,
                    original_text=request.text
                )
            except OpenAIError as e:
                logger.error(f"Overall analysis failed: {str(e)}")
        
        if request.individual_analysis:
            try:
                individual_analyses = await analyze_all_translations(
                    translations=translations,
                    original_text=request.text
                )
            except OpenAIError as e:
                logger.error(f"Individual analyses failed: {str(e)}")
        
        return AutoTranslationResponse(
            translations=translations,
            detected_source_lang=detected_lang,
            analysis=analysis,
            individual_analyses=individual_analyses
        )
    except TranslationError as e:
        raise HTTPException(status_code=400, detail=str(e))