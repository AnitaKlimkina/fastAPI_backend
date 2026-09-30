from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Users
from app.db.schemas import AboutUserResponse, BaseResponse
from app.api.deps import get_user_by_api_key

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/{id}/follow", response_model=BaseResponse)
async def user_follow_user_by_id(
        id: int,
        id_user: int = Depends(get_user_by_api_key),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint let user follows other user by his id
    """
    if id_user == id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    res = await db.execute(
        select(Users)
        .options(selectinload(Users.following))
        .where(Users.id_user==id_user)
    )
    cur_user = res.scalar_one_or_none()

    res = await db.execute(
        select(Users)
        .where (Users.id_user==id)
    )
    followed_user = res.scalar_one_or_none()
    if followed_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if followed_user in cur_user.following:
        raise HTTPException(status_code=400, detail="Already following")

    cur_user.following.append(followed_user)
    await db.commit()

    return BaseResponse(result=True)


@router.delete("/{id}/follow", response_model=BaseResponse)
async def cancel_follow_user_by_id(
        id: int,
        id_user: int = Depends(get_user_by_api_key),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint cancel follow other user by his id
    """
    res = await db.execute(
        select(Users)
        .options(selectinload(Users.following))
        .where(Users.id_user == id_user)
    )
    cur_user = res.scalar_one_or_none()

    res = await db.execute(
        select(Users)
        .where(Users.id_user==id)
    )
    followed_user = res.scalar_one_or_none()
    if followed_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if followed_user not in cur_user.following:
        raise HTTPException(status_code=404, detail="Follow not found")

    cur_user.following.remove(followed_user)
    await db.commit()

    return BaseResponse(result=True)


@router.get("/me", response_model=AboutUserResponse)
async def get_info_about_me(
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint give all info about me
    """
    res = await db.execute(
        select(Users)
        .options(
            selectinload(Users.followers),
            selectinload(Users.following),
        )
        .where(Users.api_key == api_key))
    user = res.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return AboutUserResponse(result=True, user=user)


@router.get("/{id}", response_model=AboutUserResponse)
async def get_info_about_user(
        id: int,
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint give all info about user by his id
    """
    res = await db.execute(
        select(Users)
        .options(
            selectinload(Users.followers),
            selectinload(Users.following),
        )
        .where(Users.id_user == id))
    user = res.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return AboutUserResponse(result=True, user=user)
