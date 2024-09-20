import asyncio
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def with_retry(max_attempts=10, delay=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt_count = 0
            while attempt_count < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt_count += 1
                    logging.error(f"Attempt {attempt_count} failed with error: {e}")
                    await asyncio.sleep(delay)
            else:
                logging.error("Max attempts reached. Operation failed.")
                return None

        return wrapper

    return decorator
