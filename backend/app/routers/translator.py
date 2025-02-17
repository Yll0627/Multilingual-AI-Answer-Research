from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List
from ..core.translator_service import (
    translate_to_multiple, 
    translate_responses_to_english,
    TranslationError
)
from ..core.openai_service import analyze_translations, ask_gpt_all, OpenAIError
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
    question_response: bool = Field(
        default=False,
        description="Whether to get responses for each translation as questions"
    )

class AutoTranslationResponse(BaseModel):
    translations: Dict[str, str]
    detected_source_lang: str
    analysis: str | None = None
    question_responses: Dict[str, str] | None = None
    english_responses: Dict[str, str] | None = None

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
        question_responses = None
        english_responses = None
        
        if request.analyze:
            try:
                analysis = await analyze_translations(
                    translations=translations,
                    original_text=request.text
                )
            except OpenAIError as e:
                logger.error(f"Overall analysis failed: {str(e)}")
        
        if request.question_response:
            try:
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
            analysis=analysis,
            question_responses=question_responses,
            english_responses=english_responses
        )
    except TranslationError as e:
        raise HTTPException(status_code=400, detail=str(e))