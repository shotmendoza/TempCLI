import uuid
from datetime import datetime, timedelta

import numpy as np
import pytest
import pandas as pd

from helpers.component_helpers import MainComponents
from tempcli.core.components.alias_map import AliasMap


# reproducibility
rng = np.random.default_rng(seed=42)


@pytest.fixture
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


@pytest.fixture
def basic_dataframe() -> pd.DataFrame:
    data = {
        "iid": [1000, 1001, 1002, 1003, 1004, 1005],
        "start date": ["2025-01-02", "2025-03-04", "2025-05-16", "2025-11-11", "2025-03-13", "2025-07-24"],
        "end date": ["2026-01-02", "2026-03-04", "2026-05-16", "2026-11-11", "2026-03-13", "2026-07-24"],
        "price": [100.00, 200.01, 30.03, 304.20, 23.99, 89.11],
        "cool_price": [150.00, 100.01, 2039.03, 2.20, 40.99, 289.11]
    }
    return pd.DataFrame(data)


@pytest.fixture
def empty_dataframe() -> pd.DataFrame:
    return pd.DataFrame()


@pytest.fixture
def basic_alias_map_dict() -> dict:
    """a basic example of an alias mapping."""
    return {
        "sequence": "iid",
        "date": ["start_date", "end_date"],
        "p": ["price", "cool_price"],
    }


@pytest.fixture
def basic_alias_map() -> AliasMap:
    d = {
        "sequence": "iid",
        "date": ["start_date", "end_date"],
        "p": ["price", "cool_price"],
    }
    return AliasMap(d)


#########################
# MANAGER TEST CASES
##########################
PIPE_MIXIN_STANDARD_TEST_CASES = [
    pytest.param(
        MainComponents.default_alias_map,
        MainComponents.default_ds,
        MainComponents.default_fn_obj_one_arg_series_return,
        MainComponents.default_fn_obj_one_arg_scalar_return,
        None,
        id="default_datasource_default_alias_map"
    ),
    pytest.param(
        MainComponents.bad_alias_map,
        MainComponents.default_ds,
        MainComponents.default_fn_obj_one_arg_series_return,
        MainComponents.default_fn_obj_one_arg_scalar_return,
        KeyError,
        id="default_datasource_bad_alias_map"
    ),
    pytest.param(
        MainComponents.default_alias_map,
        MainComponents.randomized_ds,
        MainComponents.default_fn_obj_one_arg_series_return,
        MainComponents.default_fn_obj_one_arg_scalar_return,
        None,
        id="randomized_datasource_default_alias"
    ),
    pytest.param(
        MainComponents.bad_alias_map,
        MainComponents.randomized_ds,
        MainComponents.default_fn_obj_one_arg_series_return,
        MainComponents.default_fn_obj_one_arg_scalar_return,
        KeyError,
        id="randomized_datasource_bad_alias"
    )
]
"""alias, datasource, f1, f2, err

alias_map values
`default_alias` = {`arg`: [`start date`, `category`]}
`bad_alias` = {`total_price`: `tp`} => column doesn't exist

Function parameters
`default_fn_obj_one_arg_series_return`: arg
`default_fn_obj_one_arg_scalar_return`: arg

"""

