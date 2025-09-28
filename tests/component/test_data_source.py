from uuid import uuid5, UUID

import pandas as pd
import pytest
from _pytest.fixtures import TopRequest

from tempcli.core.components.data import DataSource


@pytest.mark.parametrize("name,value,expected", [
    pytest.param("starter", "basic_dataframe", pd.DataFrame, id="basic_dataframe"),
    pytest.param("starter", None, ValueError, id="None as value"),
    pytest.param("starter", "empty_dataframe", ValueError, id="empty df as value"),
    pytest.param("starter", 13, TypeError, id="int as value"),
    pytest.param(54234, "basic_dataframe", TypeError, id="int as name")
]
)
def test_data_source_init_value_param(request: TopRequest, name, value, expected):
    """test to ensure that a datasource raises an error when expected, and initializes
    correctly."""
    v = None
    match value:
        case "basic_dataframe" | "empty_dataframe":
            v = request.getfixturevalue(value)
        case _:
            v = value

    if issubclass(expected, Exception):
        with pytest.raises(expected):
            ds = DataSource(name, v)
            foo = ds.data
    else:
        ds = DataSource(name, v)
        assert isinstance(ds.data, expected)


@pytest.mark.parametrize("name,value,expected", [
    pytest.param("starter", "basic_dataframe", list, id="basic_dataframe"),
    pytest.param("starter", None, ValueError, id="None as value"),
    pytest.param("starter", "empty_dataframe", ValueError, id="empty df as value"),
    pytest.param("starter", 13, TypeError, id="int as value"),
    pytest.param(54234, "basic_dataframe", TypeError, id="int as name")
]
)
def test_data_source_columns(request: TopRequest, name, value, expected):
    """test to ensure that datasource raises an error when expected, and returns the columns"""
    v = None
    match value:
        case "basic_dataframe" | "empty_dataframe":
            v = request.getfixturevalue(value)
        case _:
            v = value

    if issubclass(expected, Exception):
        with pytest.raises(expected):
            ds = DataSource(name, v)
            foo = ds.data
    else:
        ds = DataSource(name, v)
        assert isinstance(ds.columns, expected)


@pytest.mark.parametrize("name,value,expected", [
    pytest.param(
        "starter",
        "basic_dataframe",
        "06eb01d0-dd60-559a-b3b6-5a609ec1821c",
        id="basic_dataframe"),
    pytest.param(
        "starter",
        "random_dataframe",
        "06eb01d0-dd60-559a-b3b6-5a609ec1821c",
        id="identical"),
]
)
def test_data_source_key(request: TopRequest, name, value, expected):
    """test to confirm the behavior of the UUID.

    The key I get on `starter` is 06eb01d0-dd60-559a-b3b6-5a609ec1821c.
    Will check against that on subsequent calls to see if we get consistency.
    """
    v = request.getfixturevalue(value)
    ds = DataSource(name, v)

    print(ds.key)

    if request.node.nodeid == "basic_dataframe":
        assert ds.key == UUID(expected)  # will always be same key based on the name
        assert uuid5(ds.key, expected) != ds.key  # creating a new key
    else:
        assert ds.key == UUID(expected)
