"""component level conftest fixtures"""
import pandas as pd
import pytest

from helpers.component_helpers import MainComponents
from helpers.function_helpers import fn_with_args_return_df, fn_with_args_return_bool_series, fn_scalar_arg_return_bool

#########################
# FUNCTION TEST CASES
##########################
FN_STANDARD_FUNCTION_CASES = [
    pytest.param(
        fn_with_args_return_df,
        5,
        None,
        id="green_case_fn_with_args_return_df"),
    pytest.param(
        fn_with_args_return_bool_series,
        pd.Series([True, False]),
        None,
        id="green_case_fn_with_args_return_bool_series"),
    pytest.param(
        fn_scalar_arg_return_bool,
        "foo",
        None,
        id="green_case_fn_scalar_arg_return_bool"),
    pytest.param(
        None,
        None,
        TypeError,
        id="red_case_none"),
]
"""expects the arguments to be func, args: dict, expected"""
