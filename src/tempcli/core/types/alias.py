"""
AliasMap has an Alias<One, Many>

```python
if:
    alias_map = {'foo': [column_a, column_b], 'bar': 'column1'}

obj AliasMap:
    Alias.One('bar', 'column1')
    Alias.Many('foo', ('column_a', 'column_b'))
```

"""
from collections.abc import Collection, Iterator
from dataclasses import dataclass

from typing_extensions import Generic, TypeVar

from tempcli.core.types.result import Result, Ok, Err

# Defining the TypeVar that Alias accepts
C = TypeVar('C', bound=Collection)  # for collections as values (One-to-Many)
S = TypeVar('S', bound=str)  # for string as values (One-to-One)


# Alias is a One or Many
class Alias(Generic[S, C]):
    """alias represent a single line on the alias_map, which holds
    the name of the parameter as the key, and the alias as the values
    """

    def is_one(self) -> bool:
        ...

    def is_many(self) -> bool:
        ...

    def record(self) -> list["Alias"]:
        """converts an alias line into a record line

        For Many, this would involve converting the list, into individual
        tuples (param, arg), meaning the param is repeated multiple times.

        For One, this would involve converting the single tuple into a list.

        If the value is a scalar, this would involve creating an itertuple
        on the DataFrame.
        """

    def convert_to_one(self) -> Iterator["One"]:
        """used with Many. Iterator function and yields a converted One."""
        raise RuntimeError("`convert_to_one` can only be used with Many.")

    def extrapolate(self, num: int) -> list["Alias"]:
        """extrapolates a `One` into a list where the length is equal to `num`."""
        raise RuntimeError("`extrapolate` can only be used with `One`.")

    def map(self, c: Collection) -> Result:
        """maps a set of columns, and returns a new Alias object for the ones that match."""
        ...


# parameter => matches with the function
# alias => matches with the columns

@dataclass(frozen=True)
class One(Alias[S, C]):
    """Represents when the mapping only has a single value for alias"""
    parameter: str
    alias: S

    def __post_init__(self):
        # Checking for type. We want this to fail if incorrect input
        if not isinstance(self.alias, str):
            raise TypeError(f"`One` cannot be a type Collection. {type(self.alias)}.")

    def is_one(self) -> bool:
        return True

    def is_many(self) -> bool:
        return False

    def record(self) -> list["One"]:
        return [self]

    def extrapolate(self, num: int) -> list["One"]:
        i = range(0, num)
        return [self for _ in i]

    def map(self, c: Collection) -> Result:
        if not isinstance(c, str):
            for v in c:
                if v == self.alias:
                    return Ok(self)
        elif isinstance(c, str):
            if c == self.alias:
                return Ok(self)
        return Err(None)


@dataclass(frozen=True)
class Many(Alias[S, C]):
    """Represents when the mapping only has multiple values for aliases"""
    parameter: str
    aliases: C

    def __post_init__(self):
        # Checking for type. We want this to fail if incorrect input
        if not isinstance(self.aliases, Collection) or isinstance(self.aliases, str):
            raise TypeError(f"`Many` must be a type Collection. {type(self.aliases)}.")

    def is_one(self) -> bool:
        return False

    def is_many(self) -> bool:
        return True

    def record(self, is_scalar: bool = False) -> list["Many"]:
        # return [(self.parameter, alias) for alias in self.aliases]
        return [self]

    def convert_to_one(self) -> Iterator[One]:
        for c in set(self.aliases):
            yield One(parameter=self.parameter, alias=c)

    def map(self, c: Collection) -> Result:
        ones = self.convert_to_one()
        if isinstance(c, Collection) and not isinstance(c, str):
            temp = []
            for o in ones:
                if o.alias in c:
                    temp.append(o)
            if len(temp) > 1:
                many = Many(self.parameter, temp)
                return Ok(many)
            elif len(temp) == 1:
                first = temp[0]
                one = One(self.parameter, first.alias)
                return Ok(one)
            else:
                return Err(None)
        elif isinstance(c, str):
            for o in ones:
                if o.alias == c:
                    return Ok(o)
        return Err(None)
