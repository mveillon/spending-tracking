import numpy as np

from src.aggregations.estimated_income_after_tax import estimated_income_after_tax

from tests.test_utils import sample_data


def test_estimated_income_after_tax():
    data = sample_data()

    income = estimated_income_after_tax(data)

    assert np.isclose(income, 9707.65, atol=200)
