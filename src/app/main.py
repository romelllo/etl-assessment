import logging
import os

import pandas as pd
import uvicorn
from fastapi import FastAPI

from src.app.api import businesses_router
from src.app.db.repository import DatabaseRepository, fill_db_from_df
from src.app.process_data import format_categories, format_timeranges

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Current script directory
DATA_INPUT_PATH = os.path.join(BASE_DIR, "../../data/sample.csv")

LOGGING_FORMAT = (
    "[%(asctime)s] [%(filename)s:%(lineno)d] | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger()

# Initialize FastAPI app
app = FastAPI()

# Include the router
app.include_router(businesses_router, prefix="/businesses")


def configure_logger() -> None:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


# Define FastAPI startup event
@app.on_event("startup")
async def startup_event():
    """
    This function runs when the FastAPI application starts.
    It will configure logging, initialize the database, and fill it with data from the CSV.
    """
    configure_logger()

    logger.info("Reading the CSV file into DataFrame")
    df = pd.read_csv(DATA_INPUT_PATH)

    format_timeranges(df)
    format_categories(df)

    repo = DatabaseRepository()
    await repo.init()
    await fill_db_from_df(repo, df)

    await repo.close()

    logger.info("Startup process completed successfully")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
