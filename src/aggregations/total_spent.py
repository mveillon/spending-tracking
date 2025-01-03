import pandas as pd

from src.utilities.column import Column
from src.utilities.read_data import read_data
from src.utilities.paths import untracked_path


def total_spent(df: pd.DataFrame) -> float:
    """
    Returns how much money was spent in total, including untracked
    expenses.

    Parameters:
        df (DataFrame): a Pandas DataFrame

    Returns:
        spent (float): the total amount spent
    """
    return (
        df[Column.PRICE.value].sum()
        + read_data(untracked_path())[Column.PRICE.value].sum()
    )
