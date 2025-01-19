import pandas as pd
from os.path import join

from sankeyflow import Sankey
import matplotlib.pyplot as plt

from src.aggregations.estimated_income_after_tax import estimated_income_after_tax
from src.utilities.read_data import read_data
from src.utilities.paths import untracked_path, get_year
from src.utilities.column import Column
from src.utilities.dictionary_ops import (
    NestedDict,
    nodes_from_dict,
    flow_array_from_dict,
)
from src.read_config.config_globals import config_globals


def sankey_flow(df: pd.DataFrame, out_dir: str):
    """
    Plots where spending went in a Sankey chart.

    Parameters:
        df (DataFrame): a Pandas DataFrame
        out_dir (str): the directory to put the plot in

    Returns:
        None
    """
    df = pd.concat([df, read_data(untracked_path())])
    total_spent = df[Column.PRICE.value].sum()

    flow: NestedDict = {
        "Saved": estimated_income_after_tax(df) - total_spent,
        "Controllable": {"Other": 0},
        "Not Controllable": {"Food": {}, "Other": 0},
    }

    cats = df.groupby([Column.CATEGORY.value])[Column.CONTROLLABLE.value].mean()

    for cat, controllable_prop in cats.items():
        this_cat = df.loc[df[Column.CATEGORY.value] == cat]
        cat_spent = this_cat[Column.PRICE.value].sum()
        cat_t = (
            cat.title()
            if cat_spent > total_spent * config_globals()["SANKEY_OTHER_THRESHOLD"]
            else "Other"
        )
        control_key = (
            "Controllable" if round(controllable_prop) == 1 else "Not Controllable"
        )

        if round(this_cat[Column.IS_FOOD.value].mean()) == 1:
            flow["Not Controllable"]["Food"][cat_t] = (
                flow["Not Controllable"]["Food"].get(cat_t, 0) + cat_spent
            )

        else:
            flow[control_key][cat_t] = flow[control_key].get(cat_t, 0) + cat_spent

    nodes = [[("Income", estimated_income_after_tax(df))], *nodes_from_dict(flow)]

    flows = [
        *[
            ("Income", dest, nodes[1][i][1], {"flow_color_mode": "source"})
            for i, dest in enumerate(flow)
        ],
        *flow_array_from_dict(flow),
    ]

    plt.clf()
    plt.figure(figsize=(15, 8))
    plt.title(f"Spending Flow for {get_year()}")

    s = Sankey(
        flows=flows,
        nodes=nodes,
    )
    s.draw()
    plt.savefig(join(out_dir, "sankey.png"))
