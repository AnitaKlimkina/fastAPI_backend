import os
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Media
from db.schemas import MediaResponse

router = APIRouter(prefix="/api/medias", tags=["media"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))


def _save_file(upload: UploadFile) -> str:
    """Сохраняет файл и возвращает уникальное имя."""
    if upload.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required",
        )
    extension = Path(upload.filename).suffix
    unique_name = f"{uuid.uuid4()}{extension}"
    file_path = UPLOAD_DIR / unique_name

    with open(file_path, "wb") as opened_file:
        file_data = upload.file.read()
        opened_file.write(file_data)

    return unique_name


@router.post("", response_model=MediaResponse)
async def save_media(
        uploaded_file: Annotated[UploadFile, File(alias="file")],
        api_key: Annotated[str, Header(alias="api-key")],
        db: Annotated[AsyncSession, Depends(get_db)],
):
    """Endpoint save medias from the tweet."""
    if uploaded_file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is required",
        )

    try:
        unique_name = _save_file(uploaded_file)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File not saved: {exc}",
        )

    new_media = Media(path=f"/uploads/{unique_name}")
    db.add(new_media)
    await db.commit()
    await db.refresh(new_media)

    return MediaResponse(result=True, media_id=new_media.id_media)
