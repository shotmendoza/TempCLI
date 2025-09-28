"""handling functions and breaking down functions"""
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property
from uuid import UUID, uuid5

import pandas as pd
from typing_extensions import Generic

from tempcli.config import TEMPCLI_NAMESPACE
from tempcli.core.support.interfaces import FnResult
from tempcli.core.types.func_component import P, R
from tempcli.core.types.result import Result, Ok, Err


@dataclass
class Fn(Generic[P, R]):
    """handles breaking down a function, getting signatures, and params.

    `callable`: Callable[P, R], a function that takes parameter P, and returns a result R.
    The result of calling it is FnResult on Ok, Exception on Err.

    `false_as_error`: bool, whether results returning False are errors
    or results returning True are errors. Defaults to False as the errors (did not pass).

    `raise_on_error`: bool, Optional flag to raise errors on __call__ if `True` or to
    return an `Err` object on `False`. Defaults to raising an Exception.

    """
    callable: Callable[P, R]
    """a function that takes parameter P, and returns a result R."""

    false_as_error: bool = False
    """optional flag for bool functions.
    Whether results returning False is an Error,
    or True is flagging an Error. Defaults to functions
    returning errors as False.
    """

    raise_on_error: bool = True
    """Optional flag to raise errors on __call__ if `True` or to
    return an `Err` object on `False`. Defaults to raising an Exception.
    """

    _FN_NAMESPACE: UUID = field(init=False)
    """used for UUID key creation"""

    # not sure if this is the best way to do this
    call_key: UUID = field(default=None, init=False)
    """returns the last run function (__call__) UUID,
    taking arg and kwargs into account"""

    def __post_init__(self):
        # For UUID creation under this class
        self._FN_NAMESPACE = uuid5(TEMPCLI_NAMESPACE, type(self).__name__)

        # Type Handling
        if not isinstance(self.callable, Callable):
            raise TypeError(f"callable must be a Callable, got {type(self.callable)}")

    @property
    def signature(self) -> inspect.Signature:
        """returns the function's signature."""
        return inspect.signature(self.callable)

    @property
    def param_names(self) -> set[str]:
        """returns the parameters of the function as a set of strings."""
        return set(self.signature.parameters.keys())

    @property
    def name(self) -> str:
        """returns the name of the function."""
        return self.callable.__name__

    @cached_property
    def key(self) -> UUID:
        """returns the key of the function."""
        return uuid5(self._FN_NAMESPACE, self.name)

    @cached_property
    def scalar_params(self) -> set[str]:
        """returns the parameters of the function that has scalar types"""
        accepted_non_scalars = (
            pd.DataFrame,
            pd.Series
        )
        foo = [p for p, pt in self.signature.parameters.items() if pt not in accepted_non_scalars]
        return set(foo)

    @cached_property
    def has_scalar_params(self) -> bool:
        """returns whether the function has a scalar parameter."""
        return len(self.scalar_params) > 0

    def _create_call_key(self, args: tuple, kwargs: dict):
        """used to generate a key for run level
        (taking the arguments and keyword arguments into account)
        """
        args = "_".join(str(arg) for arg in args)
        kwargs = "_".join(str(v) for v in kwargs.values())
        k = args + kwargs
        self.call_key = uuid5(self._FN_NAMESPACE, k)

    def __call__(
            self,
            *args: P.args,
            **kwargs: P.kwargs,
    ) -> Result[FnResult, Exception]:
        """calls the function. Returns as a Result[FnResult, Exception].
        """

        try:
            # Use BoundArguments to prep the function.
            sig = self.signature.bind_partial(*args, **kwargs)
            sig.apply_defaults()

            # generates an uuid. not 100% on if this is the best way
            self._create_call_key(sig.args, sig.kwargs)

            result = self.callable(*sig.args, **sig.kwargs)
            fn_result = FnResult(result, sig.args, sig.kwargs, self.name)
            return Ok(fn_result)
        except Exception as e:
            if self.raise_on_error:
                raise e
            else:
                return Err(e)
