import pandas as pd
import pytest
from _pytest.fixtures import TopRequest

from tempcli.core.types.result import Err, Result, Ok


@pytest.fixture(scope="module")
def generate_result():
    def _basic_return_result_fn(data: pd.DataFrame) -> Result:
        if isinstance(data, pd.DataFrame):
            return Ok(data)
        return Err(None)
    return _basic_return_result_fn


@pytest.mark.parametrize(
    "factory,data,expected",
    [
        pytest.param("generate_result", "basic_dataframe", Ok, id="basic_dataframe_ok"),
        pytest.param("generate_result", pd.DataFrame(), Ok, id="empty_dataframe_ok"),
        pytest.param("generate_result", 123, Err, id="invalid_value_err"),
        pytest.param("generate_result", None, Err, id="none_err"),
        pytest.param("generate_result", pd.Series, Err, id="invalid_series_err"),
    ],
)
def test_result_type_behavior(request: TopRequest, data, factory, expected):
    """Confirms result works as expected"""
    fn = request.getfixturevalue(factory)
    if str(data) == "basic_dataframe":
        d = request.getfixturevalue(data)
    else:
        d = data
    result = fn(d)

    # Confirm that we got the expected type
    assert isinstance(result, expected)


@pytest.mark.parametrize(
    "factory,data,expected",
    [
        pytest.param("generate_result", "basic_dataframe", "basic_dataframe", id="happy_ok"),
        pytest.param("generate_result", None, RuntimeError, id="no_data_err"),
    ],
)
def test_result_unwrap(request: TopRequest, factory, data, expected):
    """checks method for unwrap returns expected result

    :param request: used for fixtures
    :param factory: the function that generates the result
    :param data:
    :param expected:
    :return:
    """
    if str(data) == "basic_dataframe":
        d = request.getfixturevalue("basic_dataframe")
    else:
        d = data
    fn = request.getfixturevalue(factory)
    result = fn(d)

    if data:
        ex_df: pd.DataFrame = request.getfixturevalue(expected)
        df: pd.DataFrame = result.unwrap()
        assert df.shape == ex_df.shape
    else:
        with pytest.raises(expected):
            result.unwrap()  # should error out


    #
    # # Check that we can use and return valid results
    # assert fn_returns_result == Ok(True)
    # assert fn_returns_result(123) == Err(False)
    #
    # # Checks to make sure that we can use the functions
    # success = fn_returns_result(df)
    # assert success.is_ok() is True
    # assert success.is_err() is False
    # assert success.unwrap() is True
    #
    # # Checks for unsuccessful ones
    # with pytest.raises(RuntimeError):
    #     success.unwrap_err()
