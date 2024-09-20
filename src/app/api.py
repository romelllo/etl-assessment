from typing import List

from fastapi import APIRouter

from src.app.crud import (
    get_businesses_by_category,
    get_businesses_by_day,
    get_businesses_open_now,
)
from src.app.schemas import BusinessResponse

businesses_router = APIRouter()


@businesses_router.get("/category/{category_name}")
async def api_get_businesses_by_category(category_name: str) -> List[BusinessResponse]:
    return await get_businesses_by_category(category_name)


@businesses_router.get("/day/{day_of_week}")
async def api_get_businesses_by_day(day_of_week: str) -> List[BusinessResponse]:
    return await get_businesses_by_day(day_of_week)


@businesses_router.get("/open-now")
async def api_get_businesses_open_now() -> List[BusinessResponse]:
    return await get_businesses_open_now()
