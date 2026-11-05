from fastapi import Header, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Users


async def get_user_by_api_key(
        api_key: str | None = Header(None, alias="api-key"),
        db: AsyncSession = Depends(get_db)):
    if api_key is None or api_key == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is necceccary")

    res = await db.execute(
        select(Users.id_user).where(Users.api_key == api_key))
    user_id = res.scalar_one_or_none()

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key")

    return user_id
