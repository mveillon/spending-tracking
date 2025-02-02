import numpy as np
import pandas as pd
from os.path import join

from src.utilities.types import Number
from src.utilities.helpers import monthly_income, get_weeks
from src.utilities.column import Column
from src.utilities.df_common import filter_large_transactions
from src.calculations.weekly_projection import weekly_projection
from src.visualize.common import metrics_over_time


def spent_by_week(
    df: pd.DataFrame,
    out_dir: str,
    income: Number = monthly_income(),
    add_large_expenses_back: bool = False,
) -> None:
    """
    Plots spending by week smoothed out as a per month average, compared to the monthly
    income, which by default is helpers.monthly_income() with a line plot.

    Parameters:
        df (DataFrame): a Pandas DataFrame to plot
        out_dir (str): the directory to put the plots in
        income (int): the monthly income to compare spending to. Defaults to
            `helpers.monthly_income()`
        add_large_expenses_back (bool): after large expenses are filtered out, should
            they be smoothed over all the weeks and added back in.

    Returns:
        None
    """
    df, filt_total = filter_large_transactions(df)
    weeks = np.array(get_weeks(df[Column.DATE].min(), df[Column.DATE].max()))
    avgs = np.array(weekly_projection(df))
    if add_large_expenses_back:
        avgs += filt_total / avgs.shape[0]

    income_arr = np.full(len(avgs), income)
    avg_arr = np.full(len(avgs), np.average(avgs))

    metrics_over_time(
        weeks,
        {
            "actual": (avgs, "b"),
            "": (avgs, "bo"),
            "goal": (income_arr, "g"),
            "average": (avg_arr, "r"),
        },
        "Prorated spending per week",
        join(out_dir, "by_week.png"),
    )
