from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from ....db.session import get_db
from ....schemas.voice import VoiceResponse
from ....core.auth import get_current_active_user
from ....models.user import User

router = APIRouter()

@router.get("", response_model=List[VoiceResponse])
async def get_voices(
    *, 
    db: Session = Depends(get_db),
    voice_ids: str = None,
    current_user: User = Depends(get_current_active_user)
) -> List[VoiceResponse]:
    """
    Get voice details by voice IDs (comma-separated).
    If no IDs provided, returns all voices.
    """
    try:
        if voice_ids:
            voice_id_list = voice_ids.split(',')
            query = text("""
                SELECT 
                    id, voice_id, name, main_accent, description, age, gender, 
                    use_case, main_preview_url, next_page_token, language,
                    model_id, lang_accent, locale, lang_preview_url, source
                FROM [voicebot].[dbo].[ElevenLabsVoices]
                WHERE voice_id IN (SELECT value FROM STRING_SPLIT(:voice_ids, ','))
            """)
            result = db.execute(query, {'voice_ids': voice_ids})
        else:
            query = text("""
                SELECT 
                    id, voice_id, name, main_accent, description, age, gender, 
                    use_case, main_preview_url, next_page_token, language,
                    model_id, lang_accent, locale, lang_preview_url, source
                FROM [voicebot].[dbo].[ElevenLabsVoices]
            """)
            result = db.execute(query)
        
        voices = result.fetchall()
        if not voices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No voices found"
            )
        columns = result.keys()
        return [VoiceResponse(**{col: row[idx] for idx, col in enumerate(columns)}) for row in voices]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
