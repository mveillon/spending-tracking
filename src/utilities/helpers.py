import locale
import pandas as pd
from os.path import join
from typing import List
from datetime import timedelta, date
import json

from src.utilities.read_data import combined_df
from src.utilities.paths import sheet_dir, staging_dir, income_path
from src.utilities.column import Column


def monthly_income() -> float:
    """
    Returns the monthly income this year.

    Parameters:
        None

    Returns:
        income (float): how much income was made each month
    """
    with open(income_path(), "r") as income:
        return float(income.readline().strip()) / 12


def format_currency(money: float) -> str:
    """
    Formats the currency nicely.

    Parameters:
        money (float): the amount of money

    Returns:
        formatted (str): the same number formatted into a
            currency string
    """
    locale.setlocale(locale.LC_ALL, "")
    return locale.currency(money, grouping=True)


def get_weeks(min_day: date, max_day: date) -> List[date]:
    """
    Generates the first day of every week between `min_day` and `max_day`,
    both inclusive.

    Parameters:
        min_day (date): the first day in the range
        max_day (date): the last day in the range

    Returns:
        weeks (List[date]): starting with `min_day`, generates a list
            of the first day each week until and possibly including
            `max_day`
    """
    one_week = timedelta(weeks=1)
    all_dates = [min_day]

    while all_dates[-1] < max_day:
        all_dates.append(all_dates[-1] + one_week)

    return all_dates[:-1]


def get_months(min_day: date, max_day: date) -> List[date]:
    """
    Generates the first day of every month between `min_day` and `max_day`,
    both inclusive.

    Parameters:
        min_day (date): the first day in the range
        max_day (date): the last day in the range

    Returns:
        months (List[date]): starting with `min_day`, generates a list
            of the first day each month until and possibly including
            `max_day`
    """
    all_dates = [date(min_day.year, min_day.month, min(min_day.day, 28))]

    while all_dates[-1] < max_day:
        new_year = int(all_dates[-1].month == 12)
        all_dates.append(
            date(
                all_dates[-1].year + new_year,
                all_dates[-1].month + 1 - 12 * new_year,
                all_dates[-1].day,
            )
        )

    return all_dates[:-1]


def find_big_bills():
    """
    Generates a JSON with all big bills using all spreadsheets in
    `utils.sheet_dir()`, writing the result to `utils.csv_dir()`.

    Parameters:
        None

    Returns:
        None
    """
    res = {}
    df = combined_df(sheet_dir())
    big_bills = df.loc[
        (df[Column.PRICE.value] >= 100) & (df[Column.CATEGORY.value] == "Bills")
    ]
    for _, bill in big_bills.reset_index().iterrows():
        month = bill[Column.DATE.value].strftime("%B")
        if month in res:
            res[month][bill[Column.DESCRIPTION.value]] = bill[Column.PRICE.value]
        else:
            res[month] = {bill[Column.DESCRIPTION.value]: bill[Column.PRICE.value]}

    with open(join(staging_dir(), "bills.json"), "w") as out:
        json.dump(res, out)


def time_filter(df: pd.DataFrame, min_date: str, max_date: str) -> pd.DataFrame:
    """
    Finds purchases made between min_date and max_date and
    returns the filtered Dataframe.
    e.g. `time_filter(df, '1/2/24', '1/6/24')`

    Parameters:
        df (DataFrame): the Pandas DataFrame to filter
        min_date (str): the minimum date to look for
        max_date (str): the maximum date to look for

    Returns:
        df (DataFrame): `df` filtered to be between `min_date` and `max_date`
    """
    return df.loc[
        (df[Column.DATE.value] >= min_date) & (df[Column.DATE.value] < max_date)
    ]
