import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from helpers.function_helpers import fn_scalar_arg_return_bool, fn_with_args_return_bool_series
from tempcli.core.components.alias_map import AliasMap
from tempcli.core.components.data import DataSource
from tempcli.core.components.func import Fn


rng = np.random.default_rng(seed=45)


# "User Defined" Alias Dictionaries
dict_across_df = {"arg": ["start date", "category"]}
dict_no_matching_param = {"total_price": "tp"}


# DataFrames
def basic_dataframe() -> pd.DataFrame:
    data = {
        "iid": [1000, 1001, 1002, 1003, 1004, 1005],
        "start date": ["2025-01-02", "2025-03-04", "2025-05-16", "2025-11-11", "2025-03-13", "2025-07-24"],
        "end date": ["2026-01-02", "2026-03-04", "2026-05-16", "2026-11-11", "2026-03-13", "2026-07-24"],
        "price": [100.00, 200.01, 30.03, 304.20, 23.99, 89.11],
        "cool_price": [150.00, 100.01, 2039.03, 2.20, 40.99, 289.11]
    }
    return pd.DataFrame(data)


def random_dataframe():
    n_rows = 10

    df = pd.DataFrame({
        "name": rng.choice(["Alice", "Bob", "Charlie", "Dana"], size=n_rows),
        "age": rng.integers(20, 60, size=n_rows),
        "score": rng.normal(loc=75, scale=10, size=n_rows).round(1),
        "date": [
            datetime.today().date() - timedelta(days=int(d))
            for d in rng.integers(0, 30, size=n_rows)
        ],
        "category": rng.choice(["A", "B", "C"], size=n_rows),
        # example UUID field
        "uuid_key": [uuid.uuid4() for _ in range(n_rows)],
    })
    return df


class MainComponents:
    # Function Components
    default_fn_obj_one_arg_series_return: Fn = Fn(fn_with_args_return_bool_series)
    default_fn_obj_one_arg_scalar_return: Fn = Fn(fn_scalar_arg_return_bool)

    # DataSource Components
    default_ds = DataSource(name="basic_datasource", value=basic_dataframe())
    randomized_ds = DataSource(name="randomized_datasource", value=random_dataframe())

    # AliasMap Components
    default_alias_map = AliasMap(dict_across_df)
    bad_alias_map = AliasMap(dict_no_matching_param)
