import pytest
from _pytest.fixtures import TopRequest

from tempcli.core.components.alias_map import AliasMap
from tempcli.core.types.result import Err, Ok


# TODO: Need to add some checks on AliasMapping overwriting existing params and columns
# TODO: Need to add some checks on AliasMapping for one dataframe with multiple columns with one param


####################
# BASIC INIT TESTS
####################
@pytest.mark.parametrize("m,expected", [
    pytest.param("basic_alias_map_dict", None, id="init_happy_path"),
    pytest.param({}, ValueError, id="init_empty_dict"),
    pytest.param(None, TypeError, id="init_error"),
]
)
def test_alias_map_init(request: TopRequest, m, expected):
    """test to ensure that alias map initializes correctly"""
    if m:
        am = request.getfixturevalue(m)
        a = AliasMap(am)
        assert isinstance(a, AliasMap)
    else:
        with pytest.raises(expected):
            AliasMap(m)


###################
# Functionality
###################
@pytest.mark.parametrize("columns,match,expected", [
    pytest.param(
        "basic_dataframe",
        False,
        {'cool_price', 'price', 'iid'},
        id="init_happy_path_no_match"
    ),
    pytest.param(
        "basic_dataframe",
        True,
        {'cool_price', 'price', 'iid'},
        id="init_happy_path_match"
    ),
    pytest.param(None, False, TypeError, id="error_wrong_type"),
    pytest.param(None, True, TypeError, id="error_wrong_type_match"),
    pytest.param(
        "empty_dataframe",
        True,
        Err,
        id="error_empty_dataframe"
    ),
]
)
def test_check_columns(request: TopRequest, columns, match, expected):
    """testing alias_map's check_columns function"""
    alias_map = request.getfixturevalue("basic_alias_map")

    if columns:
        data = request.getfixturevalue(columns)
        r = alias_map.check_columns(columns=data.columns, match_column=match)

        if columns == "empty_dataframe":
            assert isinstance(r, Err)
        else:
            assert r.unwrap() == expected
            assert isinstance(r, Ok)
    else:
        with pytest.raises(expected):
            alias_map.check_columns(columns=None, match_column=match)


@pytest.mark.parametrize("p,raise_error,expected", [
    pytest.param(
        ["iid", "price"],
        False,
        (Ok, ['iid', 'price']),
        id="param_happy_path_no_match"
    ),
    pytest.param(
        [],
        False,
        (Err, []),
        id="param_empty_list"
    ),
    pytest.param(
        "iid",
        False,
        [Ok, ["iid"]],
        id="param_single_string"
    ),
    pytest.param(None, True, TypeError, id="error_raise_missing_None"),
    pytest.param(["obviously_missing", "No Column"], True, KeyError, id="error_raise_missing"),
    pytest.param([], True, ValueError, id="error_raise_empty_list"),
]
)
def test_check_params(request: TopRequest, p, raise_error, expected):
    """should raise or log an exception if there are expected columns missing
    or a function wouldn't run because a column is missing.
    """
    alias_map: AliasMap = request.getfixturevalue("basic_alias_map")

    if raise_error:
        with pytest.raises(expected):
            r = alias_map.check_params(params=p, raise_missing=raise_error)
            assert r.unwrap() == expected
    else:
        r = alias_map.check_params(params=p, raise_missing=raise_error)
        if not request.node.callspec.id == "param_empty_list":
            assert r.unwrap() == expected[1]
            assert isinstance(r, expected[0])
        else:
            assert r.is_err()
