"""we'll start storing types we think are important here"""
from abc import ABC, abstractmethod
from collections.abc import Callable, Collection
from dataclasses import dataclass

from typing_extensions import Generic, TypeVar, Any

# Defining the Type Vars for Result
T = TypeVar("T", covariant=True)  # type T
E = TypeVar("E", covariant=True)  # Error E
U = TypeVar("U")  # similar to T, but is used for chaining, since the next Result may be different


# Defining the Result Type -> Generic here meaning, Result is either a valid T or an error E
# We'll start by only implementing the important ones to start.
class Result(Generic[T, E], ABC):
    """similar to the Rust result, will take in whatever a function returns.
    If a function raises an exception, the Exception will be stored under an `Result.Err`.
    If the expected value or workable value comes back, the result will be stored under `Ok`.
    """
    @property
    @abstractmethod
    def is_ok(self) -> bool:
        """Returns whether the value is valid and a successful type."""
        raise NotImplementedError()

    @property
    def is_err(self) -> bool:
        """Returns whether the value is invalid and errored."""
        return not self.is_ok

    @abstractmethod
    def unwrap(self) -> T:
        """Returns the successful value."""
        raise NotImplementedError()

    @abstractmethod
    def unwrap_or(self, default: Any) -> T:
        """Returns the valid value or a default value if the result was an error."""
        raise NotImplementedError()

    @abstractmethod
    def unwrap_err(self) -> E:
        """Returns the error value."""
        raise NotImplementedError()

    @abstractmethod
    def and_then(self, f: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """Used for chaining multiple result functions together:

        parse_int("5").and_then(reciprocal)

        :param f: a callable function that takes a Result
        :return: returns a Result
        """
        raise NotImplementedError()


@dataclass(frozen=True, slots=True)
class Ok(Result[T, Any], Generic[T]):
    """The successful value of a Result"""
    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: Any) -> T:
        return self.value

    def unwrap_err(self) -> E:
        raise RuntimeError(f"Unwrap failed. Called unwrap_err on Success: {self.value}")

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return f(self.value)


@dataclass(frozen=True, slots=True)
class Err(Result[Any, E], Generic[E]):
    """The failed value of a Result"""
    err: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> T:
        raise RuntimeError(f"Unwrap failed. Called unwrap on Error: {self.err}")

    def unwrap_or(self, default: Any) -> T:
        return default

    def unwrap_err(self) -> E:
        return self.err

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return f(self.err)


# Something that works on Python 3.12 and after
# type Result[T, E] = Ok[T] | Err[E]
