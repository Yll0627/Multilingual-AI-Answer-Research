from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List
from ..core.translator_service import translate_to_multiple, TranslationError

router = APIRouter()

class AutoTranslationRequest(BaseModel):
    text: str
    target_langs: List[str] = Field(
        default=["EN", "DE", "FR", "JA"],
        description="List of target language codes"
    )

class AutoTranslationResponse(BaseModel):
    translations: Dict[str, str]
    detected_source_lang: str

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
        return AutoTranslationResponse(
            translations=translations,
            detected_source_lang=detected_lang
        )
    except TranslationError as e:
        raise HTTPException(status_code=400, detail=str(e)) 