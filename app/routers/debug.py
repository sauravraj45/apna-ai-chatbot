from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

router = APIRouter(
    prefix="/debug",
    tags=["Debug"]
)


@router.get("/user/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT id, fullName, email
            FROM users
            WHERE id = :id
        """),
        {"id": user_id},
    )

    return result.mappings().first()


@router.get("/orders/{user_id}")
async def get_orders(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT *
            FROM orders
            WHERE user_id = :id
            ORDER BY id DESC
        """),
        {"id": user_id},
    )

    return result.mappings().all()


@router.get("/addresses/{user_id}")
async def get_addresses(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT *
            FROM addresses
            WHERE user_id = :id
            ORDER BY id DESC
        """),
        {"id": user_id},
    )

    return result.mappings().all()