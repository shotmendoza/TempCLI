"""test behavior for alias mapping"""
import py

import pytest
from _pytest.fixtures import TopRequest

from tempcli.core.types.alias import One, Many


# Testing the components of the AliasMap
@pytest.mark.parametrize(
    "parameter, expected_err",
    [
        pytest.param("sequence", None, id="happy_path"),
        pytest.param("p", TypeError, id="raises_type_error"),
    ],
)
def test_one_init(request: TopRequest, parameter, expected_err):
    """we would expect a pass for single values and fail for a collection"""
    alias_map = request.getfixturevalue("basic_alias_map_dict")
    val = alias_map[parameter]

    if expected_err:
        with pytest.raises(expected_err):
            One(parameter, val)
    else:
        one = One(parameter, val)
        assert isinstance(one, One)


@pytest.mark.parametrize(
    "parameter, expected_err",
    [
        pytest.param("sequence", TypeError, id="raises_type_error"),
        pytest.param("p", None, id="happy_path"),
    ]
)
def test_many_init(request: TopRequest, parameter, expected_err):
    """we would expect a pass for single values and fail for a collection"""
    alias_map = request.getfixturevalue("basic_alias_map_dict")
    val = alias_map[parameter]

    if expected_err:
        with pytest.raises(expected_err):
            Many(parameter, val)
    else:
        many = Many(parameter, val)
        assert isinstance(many, Many)


def test_many_to_one_conversion(request: TopRequest):
    """should test to confirm that initializing the AliasMap
    correctly identifies when something is One (One-to-One) or Many (One-to-Many).
    """
    alias_map = request.getfixturevalue("basic_alias_map_dict")
    many = Many("p", alias_map["p"])

    many_ones = [o for o in many.convert_to_one()]
    assert all((isinstance(o, One) for o in many_ones))
