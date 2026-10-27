from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Users
from db.schemas import AboutUserResponse, BaseResponse
from api.deps import get_user_by_api_key


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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself")
    res = await db.execute(
        select(Users)
        .options(selectinload(Users.following))
        .where(Users.id_user == id_user)
    )
    cur_user = res.scalar_one_or_none()
    if cur_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key")

    res = await db.execute(
        select(Users)
        .where(Users.id_user == id)
    )
    followed_user = res.scalar_one_or_none()

    if followed_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")
    if followed_user in cur_user.following:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following")

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
    if cur_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key")

    res = await db.execute(
        select(Users)
        .where(Users.id_user == id)
    )
    followed_user = res.scalar_one_or_none()
    if followed_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")
    if followed_user not in cur_user.following:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow not found")

    cur_user.following.remove(followed_user)
    await db.commit()

    return BaseResponse(result=True)


@router.get("/me", response_model=AboutUserResponse)
async def get_info_about_me(
        id_user: int = Depends(get_user_by_api_key),
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
        .where(Users.id_user == id_user))
    user = res.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key")

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")

    return AboutUserResponse(result=True, user=user)
