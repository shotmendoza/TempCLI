import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# reproducibility
rng = np.random.default_rng(seed=41)


class Help:
    def __init__(self):
        self.name = "object"

    def fn_obj(self) -> str:
        return self.name

    @classmethod
    def fn_cls(cls) -> str:
        return "class"

    @staticmethod
    def fn_static() -> str:
        return "static"


def empty_fn_return_int() -> int:
    """a basic example of a function."""
    return 1


def empty_fn_return_float() -> float:
    """a basic example of a function."""
    return 1.0


def fn_with_args_float(start: float, end: float) -> float:
    """a basic example of a function."""
    return float(start + end)


def fn_scalar_arg_return_bool(arg: str) -> bool:
    """a basic example of a function."""
    return arg == "foo"


def fn_with_args_return_bool_series(arg: pd.Series) -> pd.Series:
    """fn with series arguments and returns boolean series"""
    foo = [rng.choice([True, False]) for _ in range(len(arg))]
    return pd.Series(foo)


def fn_no_return_type():
    """fn with no args and no return type"""
    return bool


def fn_with_args_return_df(row: int = 5) -> pd.DataFrame:
    """fn with args and returns a DataFrame"""
    df = pd.DataFrame({
        "name": rng.choice(["Alice", "Bob", "Charlie", "Dana"], size=row),
        "age": rng.integers(20, 60, size=row),
        "score": rng.normal(loc=75, scale=10, size=row).round(1),
        "date": [
            datetime.today().date() - timedelta(days=int(d))
            for d in rng.integers(0, 30, size=row)
        ],
        "category": rng.choice(["A", "B", "C"], size=row),
        # example UUID field
        "uuid_key": [uuid.uuid4() for _ in range(row)],
    })
    return df
