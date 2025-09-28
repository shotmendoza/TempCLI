from collections.abc import Callable

import pytest
from _pytest.fixtures import TopRequest

from component.conftest import FN_STANDARD_FUNCTION_CASES
from helpers.function_helpers import fn_with_args_return_df, fn_with_args_return_bool_series, fn_scalar_arg_return_bool, Help
from tempcli.core.components.func import Fn
from tempcli.core.types.result import Ok


@pytest.mark.parametrize("c, expected", [
    pytest.param(fn_with_args_return_df, None, id="fn_with_args_df"),
    pytest.param(fn_with_args_return_bool_series, None, id="fn_return_bool_series_arg"),
    pytest.param(fn_scalar_arg_return_bool, None, id="fn_return_bool"),
    pytest.param(None, TypeError, id="none as arg"),
    pytest.param("not fn", TypeError, id="string as arg"),
    pytest.param(Help, None, id="string as arg"),
]
)
def test_fn_init(request: TopRequest, c, expected):
    if isinstance(c, Callable):
        f = Fn(callable=c)
        assert f.name == c.__name__
    else:
        if isinstance(c, Help):
            fc = Fn(callable=c.fn_cls)
            assert fc() == "class"

            fs = Fn(callable=c.fn_static)
            assert fs() == "static"

            h = Help()
            fo = Fn(callable=h.fn_obj)
            assert fo() == "object"
        else:
            with pytest.raises(TypeError):
                Fn(callable=c)


@pytest.mark.parametrize("c, arg, expected", FN_STANDARD_FUNCTION_CASES)
def test_fn_calls(request: TopRequest, c, arg, expected):
    if expected is None:
        f = Fn(callable=c)
        result = f(arg)
        assert isinstance(result, Ok)
    else:
        if issubclass(expected, Exception):
            with pytest.raises(expected):
                f = Fn(callable=c)
                f(arg)
