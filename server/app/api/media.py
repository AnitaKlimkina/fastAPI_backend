import uuid
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Header, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Media
from db.schemas import MediaResponse
from db.database import get_db

router = APIRouter(prefix="/api/medias", tags=["media"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))

@router.post("", response_model=MediaResponse)
async def save_media(
        file: UploadFile=File(...),
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint save medias from the tweet
    """
    if file is None:
        raise HTTPException(status_code=400, detail="File is required")

    extension = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{extension}"
    file_path = UPLOAD_DIR / unique_name

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File not saved: {e}")

    new_media = Media(path=f"/uploads/{unique_name}")
    db.add(new_media)
    await db.commit()
    await db.refresh(new_media)

    return MediaResponse(result=True, media_id=new_media.id_media)
