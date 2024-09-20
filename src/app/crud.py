import logging
from datetime import datetime
from typing import List

from fastapi import HTTPException
from tortoise.expressions import Q

from src.app.db.models import Business
from src.app.schemas import BusinessHoursBase, BusinessResponse, CategoryBase

logger = logging.getLogger(__name__)


async def get_businesses_by_category(category_name: str) -> List[BusinessResponse]:
    """
    Fetch businesses that belong to the given category.

    Args:
        category_name (str): The name of the category to filter by.

    Returns:
        List[BusinessResponse]: A list of businesses that belong to the specified category.

    Raises:
        HTTPException: If no businesses are found for the given category.
    """
    logger.info(f"Fetching businesses for category: {category_name}")
    businesses = await Business.filter(
        categories__category=category_name
    ).prefetch_related("hours", "categories")

    if not businesses:
        logger.warning(f"No businesses found for category: {category_name}")
        raise HTTPException(
            status_code=404, detail="No businesses found for this category"
        )

    response = []
    for business in businesses:
        categories = [
            CategoryBase.from_orm(category) for category in business.categories
        ]
        hours = [BusinessHoursBase.from_orm(hour) for hour in business.hours]

        # Check if the business is closed
        is_closed = all(
            (hour.shift1_start == "00:00" and hour.shift1_end == "00:00")
            and (hour.shift2_start == "00:00" and hour.shift2_end == "00:00")
            for hour in hours
        )

        if is_closed:
            continue  # Skip this business if it's closed

        response.append(
            BusinessResponse(
                id=business.id,
                timezone=business.timezone,
                rating=business.rating,
                max_rating=business.max_rating,
                review_count=business.review_count,
                categories=categories,
                hours=hours,
            )
        )

    logger.info(f"Found {len(response)} businesses for category: {category_name}")

    return response


async def get_businesses_by_day(day_of_week: str) -> List[BusinessResponse]:
    logger.info(f"Fetching businesses open on: {day_of_week}")

    days_map = {
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        "sunday": "Sunday",
    }

    day = days_map.get(day_of_week.lower())
    if not day:
        logger.error(f"Invalid day of the week: {day_of_week}")
        raise HTTPException(status_code=400, detail="Invalid day of the week")

    businesses = await Business.filter(hours__day=day).prefetch_related(
        "hours", "categories"
    )

    if not businesses:
        logger.warning(f"No businesses found open on: {day_of_week}")
        raise HTTPException(
            status_code=404, detail="No businesses found open on this day"
        )

    response = []
    for business in businesses:
        categories = [
            CategoryBase.from_orm(category) for category in business.categories
        ]
        hours = [BusinessHoursBase.from_orm(hour) for hour in business.hours]

        # Check if the business is closed
        is_closed = all(
            (hour.shift1_start == "00:00" and hour.shift1_end == "00:00")
            and (hour.shift2_start == "00:00" and hour.shift2_end == "00:00")
            for hour in hours
        )

        if is_closed:
            continue  # Skip this business if it's closed

        response.append(
            BusinessResponse(
                id=business.id,
                timezone=business.timezone,
                rating=business.rating,
                max_rating=business.max_rating,
                review_count=business.review_count,
                categories=categories,
                hours=hours,
            )
        )

    logger.info(f"Found {len(response)} businesses open on: {day_of_week}")

    return response


async def get_businesses_open_now() -> List[BusinessResponse]:
    logger.info("Fetching businesses open at the current time")

    local_now = datetime.now()
    current_day = local_now.strftime("%A")  # e.g., "Monday"
    current_time = local_now.strftime("%H:%M")  # e.g., "14:30" for 2:30 PM

    businesses = await Business.filter(
        Q(hours__day=current_day)
        & (
            Q(
                hours__shift1_start__lte=current_time,
                hours__shift1_end__gte=current_time,
            )
            | Q(
                hours__shift2_start__lte=current_time,
                hours__shift2_end__gte=current_time,
            )
        )
    ).prefetch_related("hours", "categories")

    if not businesses:
        logger.warning("No businesses are open now")
        raise HTTPException(status_code=404, detail="No businesses are open now")

    response = []
    for business in businesses:
        categories = [
            CategoryBase.from_orm(category) for category in business.categories
        ]
        hours = [BusinessHoursBase.from_orm(hour) for hour in business.hours]

        # Check if the business is closed
        is_closed = all(
            (hour.shift1_start == "00:00" and hour.shift1_end == "00:00")
            and (hour.shift2_start == "00:00" and hour.shift2_end == "00:00")
            for hour in hours
        )

        if is_closed:
            continue  # Skip this business if it's closed

        response.append(
            BusinessResponse(
                id=business.id,
                timezone=business.timezone,
                rating=business.rating,
                max_rating=business.max_rating,
                review_count=business.review_count,
                categories=categories,
                hours=hours,
            )
        )

    logger.info(f"Found {len(response)} businesses open now")

    return response
