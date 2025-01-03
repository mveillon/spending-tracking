import pandas as pd
from typing import List
from datetime import datetime, timedelta

from src.utilities.helpers import get_weeks, time_filter
from src.utilities.column import Column
from src.calculations.projected_spending import projected_spending


def weekly_projection(df: pd.DataFrame) -> List[float]:
    """
    Finds the monthly spending projection for each week.

    Parameters:
        df (DataFrame): the Pandas DataFrame to analyze

    Returns:
        week_spent (List[float]): how much was spent per week,
            projected as a per_month total
    """
    fmt = "%m/%d/%Y"
    one_week = timedelta(weeks=1)
    all_dates = get_weeks(df[Column.DATE.value].min(), df[Column.DATE.value].max())

    avgs = []
    for i in range(len(all_dates)):
        week_df = time_filter(
            df,
            datetime.strftime(all_dates[i], fmt),
            datetime.strftime(all_dates[i] + one_week, fmt),
        )

        avgs.append(
            projected_spending(
                week_df,
                week_df[Column.DATE.value].max().strftime("%B"),
                total_days=one_week.days,
            )
            if week_df.shape[0] > 0
            else 0
        )

    return avgs
