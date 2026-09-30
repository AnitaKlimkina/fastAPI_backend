from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Users

async def get_user_by_api_key(api_key: str = Header(..., alias="api-key"), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Users.id_user).where(Users.api_key == api_key))
    user_id = res.scalar_one_or_none()

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user_id