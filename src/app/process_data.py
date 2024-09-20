import logging
import re
from datetime import datetime

import pandas as pd

from src.app.constants import DAYS_OF_WEEK

logger = logging.getLogger(__name__)


def normalize_dashes(time_range: str) -> str:
    """
    Normalize various types of dashes and hyphens to a standard dash '-'.
    Args:
        time_range (str): A string containing the time range.
    Returns:
        str: The normalized string with consistent dashes.
    """
    return re.sub(r"[—–−‒―]", "-", time_range)


def fix_irregular_time_format(t: str) -> str:
    """
    Fixes irregular time formats that may be missing colons (e.g., '600pm' -> '6:00pm').
    Args:
        t (str): The time string to fix.
    Returns:
        str: Corrected time string with colon (if needed).
    """
    match = re.match(r"^(\d{1,2})(\d{2})(am|pm)$", t)
    if match:
        return f"{match.group(1)}:{match.group(2)}{match.group(3)}"
    return t


def infer_missing_am_pm(start_time: str, end_time: str) -> tuple[str, str]:
    """
    Infer missing AM/PM for one side of the time range when the other side contains it.
    Args:
        start_time (str): The start time of the range.
        end_time (str): The end time of the range.
    Returns:
        tuple: Both start and end times with inferred AM/PM.
    """
    start_time = start_time.strip()
    end_time = end_time.strip()

    if "am" in start_time or "pm" in start_time:
        if not ("am" in end_time or "pm" in end_time):
            end_time += start_time[-2:]
    elif "am" in end_time or "pm" in end_time:
        start_time += end_time[-2:]

    return start_time, end_time


def convert_to_24h(t: str) -> str | None:
    """
    Converts time from 12-hour format with AM/PM to 24-hour format.
    Args:
        t (str): The time string to convert.
    Returns:
        str: Time in 24-hour format (HH:MM) or None if unrecognized format.
    """
    try:
        t = t.replace(".", ":")  # Normalize dots to colons for time parsing
        if "am" in t or "pm" in t:
            return (
                datetime.strptime(t, "%I:%M%p").strftime("%H:%M")
                if ":" in t
                else datetime.strptime(t, "%I%p").strftime("%H:%M")
            )
        else:
            return datetime.strptime(t, "%H:%M").strftime("%H:%M")
    except ValueError:
        return None


# Cleansing and processing time ranges into 24-hour format
def cleanse_time_range(time_range: str) -> list[list[str]]:
    """
    Cleanses a time range string, converts times to 24-hour format, and splits into start and end times.
    Handles various cases like missing AM/PM, irregular formatting, and closed/24 hours cases.
    Args:
        time_range (str): The time range string to process.
    Returns:
        list: A list of time range pairs, with each pair as [start_time, end_time] in 24-hour format.
    """
    if pd.isna(time_range) or time_range is None or time_range.strip() == "":
        return [["00:00", "00:00"]]

    time_range = time_range.strip().lower()

    if "24 hours" in time_range:
        return [["00:00", "23:59"]]

    if "closed" in time_range:
        return [["00:00", "00:00"]]

    time_range = re.sub(r"\u202f", "", time_range)  # Remove non-breaking spaces
    time_range = time_range.replace(" ", "")

    time_range = re.sub(r"^[:a-z]{0,4}:", "", time_range)  # Remove prefix like 'sun:'
    time_range = re.sub(r"a\.?m\.?", "am", time_range)
    time_range = re.sub(r"p\.?m\.?", "pm", time_range)

    time_range = re.sub(r"\b(\d{1,2})(\s*a)\b", r"\1am", time_range)  # '4 a' -> '4am'
    time_range = re.sub(r"\b(\d{1,2})(\s*p)\b", r"\1pm", time_range)  # '6 p' -> '6pm'

    time_range = normalize_dashes(time_range)

    time_range = time_range.replace("to", "-")
    time_range = re.sub(r"(\d{1,2}:\d{2}(am|pm))(\d{1,2}(am|pm))", r"\1-\3", time_range)
    time_range = re.sub(r"[\n,;]", "-", time_range)  # Normalize newlines and commas

    time_range = re.sub(r"--+", "-", time_range)
    time_range = re.sub(r"(\d{2}(am|pm))(\d{1,2}:\d{2}(am|pm))", r"\1-\3", time_range)

    multiple_ranges = time_range.split("-")

    times = []

    for i in range(0, len(multiple_ranges), 2):
        try:
            start_time = multiple_ranges[i]
            end_time = multiple_ranges[i + 1] if i + 1 < len(multiple_ranges) else None

            if not start_time or not end_time:
                return [["00:00", "00:00"]]

            start_time, end_time = infer_missing_am_pm(start_time, end_time)
            start_time = fix_irregular_time_format(start_time)
            end_time = fix_irregular_time_format(end_time)

            start_time_24 = convert_to_24h(start_time)
            end_time_24 = convert_to_24h(end_time)

            if start_time_24 and end_time_24:
                times.append([start_time_24, end_time_24])
        except (ValueError, IndexError):
            return [["00:00", "00:00"]]  # Invalid case, return fallback

    return times if times else [["00:00", "00:00"]]


def assign_time_shifts(df: pd.DataFrame, day: str) -> None:
    """
    For each day, extract time ranges and assign start and end times for two shifts.
    Args:
        df (pd.DataFrame): DataFrame containing time ranges for each day.
        day (str): The day of the week to process.
    Returns:
        None: Modifies the DataFrame in place by adding four new columns for two shifts (start/end).
    """
    time_ranges = df[day].apply(cleanse_time_range)

    # Create columns for each time shift (two shifts per day)
    df[f"{day}_start_time_shift1"] = time_ranges.apply(
        lambda x: x[0][0] if len(x) > 0 else "00:00"
    )
    df[f"{day}_end_time_shift1"] = time_ranges.apply(
        lambda x: x[0][1] if len(x) > 0 else "00:00"
    )

    df[f"{day}_start_time_shift2"] = time_ranges.apply(
        lambda x: x[1][0] if len(x) > 1 else "00:00"
    )
    df[f"{day}_end_time_shift2"] = time_ranges.apply(
        lambda x: x[1][1] if len(x) > 1 else "00:00"
    )


def format_timeranges(df: pd.DataFrame) -> None:
    """
    Processes time range columns in the DataFrame for each day of the week.

    This function applies time range formatting to the columns representing each
    day of the week in the DataFrame by calling the `assign_time_shifts` function.
    It splits the time ranges into shifts for each day (start and end times) and
    populates new columns for these shifts in the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing columns for each day of
                           the week, where time ranges are stored.

    Returns:
        None: The function modifies the input DataFrame in-place.
    """
    for day in DAYS_OF_WEEK:
        assign_time_shifts(df, day)

    logger.info("Formatted timeranges in DataFrame")


def format_categories(df: pd.DataFrame) -> None:
    """
    Cleans and splits the 'categories' column in the DataFrame.

    This function fills any missing values in the 'categories' column with the
    default value 'Uncategorized', and then splits the values of the 'categories'
    column on semicolons (;) into a list of individual categories. The stripped
    result is stored in a new column named 'categories_split'.

    Args:
        df (pd.DataFrame): The input DataFrame containing the 'categories' column.

    Returns:
        None: The function modifies the input DataFrame in-place.
    """
    df["categories"] = df["categories"].fillna("Uncategorized")
    df["categories_split"] = df["categories"].str.split(";")

    # Strip leading/trailing spaces from each category in the split list
    df["categories_split"] = df["categories_split"].apply(
        lambda x: [item.strip() for item in x]
    )

    logger.info("Formatted categories in DataFrame")
