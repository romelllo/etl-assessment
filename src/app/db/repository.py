import logging

import pandas as pd
from tortoise import Tortoise, exceptions
from tortoise.transactions import in_transaction

from src.app.constants import DAYS_OF_WEEK
from src.app.db.models import Business, BusinessHours, Category
from src.app.settings import settings
from src.app.utils import with_retry

logger = logging.getLogger(__name__)


class DatabaseRepository:
    def __init__(self):
        self.db_url = settings.postgresql_url

    @with_retry()
    async def init(self):
        await Tortoise.init(
            db_url=self.db_url, modules={"models": ["src.app.db.models"]}
        )
        await Tortoise.generate_schemas()
        logger.info("Database initialized successfully")

    @with_retry()
    async def insert_business(
        self,
        business_id: int,
        timezone: str,
        rating: float,
        max_rating: float,
        review_count: int,
    ) -> int:
        async with in_transaction():
            business = await Business.create(
                id=business_id,
                timezone=timezone,
                rating=rating,
                max_rating=max_rating,
                review_count=review_count,
            )
        logger.info(f"Inserted business {business_id}: {timezone}, rating: {rating}")
        return business.id

    @with_retry()
    async def insert_business_hours(
        self,
        business_id: int,
        day: str,
        shift1_start: str,
        shift1_end: str,
        shift2_start: str = None,
        shift2_end: str = None,
    ) -> None:
        try:
            business = await Business.get(id=business_id)
            await BusinessHours.create(
                business=business,
                day=day,
                shift1_start=shift1_start,
                shift1_end=shift1_end,
                shift2_start=shift2_start,
                shift2_end=shift2_end,
            )
            logger.info(f"Inserted business hours for {day} for business {business_id}")
        except exceptions.DoesNotExist:
            logger.error(f"Business with ID {business_id} does not exist")
            raise

    @with_retry()
    async def insert_categories(self, business_id: int, categories: list[str]) -> None:
        try:
            business = await Business.get(id=business_id)
            for category in categories:
                await Category.create(business=business, category=category)
                logger.info(f"Inserted category: {category} for business {business_id}")
        except exceptions.DoesNotExist:
            logger.error(f"Business with ID {business_id} does not exist")
            raise

    @with_retry()
    async def close(self) -> None:
        await Tortoise.close_connections()
        logger.info("Database connection closed successfully")


async def fill_db_from_df(repo: DatabaseRepository, df: pd.DataFrame) -> None:
    # Loop through the dataframe and insert each business record
    for index, row in df.iterrows():
        # Insert business data
        business_id = await repo.insert_business(
            business_id=row["ID"],
            timezone=row["timezone"],
            rating=row["Rating"],
            max_rating=row["Max Rating"],
            review_count=row["Review Count"],
        )

        # Insert business hours for each day
        for day in DAYS_OF_WEEK:
            await repo.insert_business_hours(
                business_id=business_id,
                day=day,
                shift1_start=row[f"{day}_start_time_shift1"],
                shift1_end=row[f"{day}_end_time_shift1"],
                shift2_start=row[f"{day}_start_time_shift2"],
                shift2_end=row[f"{day}_end_time_shift2"],
            )

        # Insert categories (if any)
        categories = (
            row["categories_split"] if isinstance(row["categories_split"], list) else []
        )
        await repo.insert_categories(business_id, categories)

    logger.info("Filled DB with data from CSV")
