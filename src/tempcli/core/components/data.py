from dataclasses import dataclass, field
from uuid import uuid5, UUID

import pandas as pd

from tempcli.config import TEMPCLI_NAMESPACE
from tempcli.core.types.result import Ok, Err, Result


@dataclass(frozen=True)
class DataSource:
    """used as a wrapper around data or a data source. For now,
    this will just be used as a placeholder, but may be expanded
    in the future, based on needs.

    `name`: str, the name of the data source

    `value`: pd.DataFrame, the data value. Defaults to None.

    """
    name: str
    value: pd.DataFrame = None
    _DATA_SOURCE_NAMESPACE: UUID = field(init=False)

    def __post_init__(self):
        # class UUID creation
        object.__setattr__(
            self,
            '_DATA_SOURCE_NAMESPACE',
            uuid5(TEMPCLI_NAMESPACE, type(self).__name__)
        )

        # checking to make sure name is ok
        if not isinstance(self.name, str):
            if isinstance(self.name, UUID) or isinstance(self.name, int):
                raise TypeError(f"Name must be a string. Try wrapping {self.name} in a string.")
            raise TypeError(f"Name must be a string. Given {type(self.name)}.")

        if not isinstance(self.value, pd.DataFrame):
            if self.value is not None:
                raise TypeError(f"Value must be a DataFrame. Given {type(self.value)}.")

    def _check_value(self) -> Result:
        """returns the given dataset. If the data is empty or None,
        will return Err(self.name), otherwise, will return Ok."""
        if self.value is None or self.value.shape[0] == 0:
            return Err(self.name)
        return Ok(self.value)

    @property
    def data(self) -> pd.DataFrame:
        """returns the data given that the value is ok."""
        value = self._check_value()
        if value.is_ok():
            return value.unwrap()
        raise ValueError(f"Can't get data for empty dataset {value.unwrap_err()}.")

    @property
    def key(self) -> UUID:
        """returns a unique key from a data source."""
        return uuid5(self._DATA_SOURCE_NAMESPACE, self.name)

    @property
    def columns(self) -> list[str]:
        """returns the dataset's columns.
        This gives a quicker way to access the data than using
        `DataSource.value.value.columns`.`

        Will raise an error on an empty dataset.
        """
        value = self._check_value()
        if value.is_ok():
            return list(self.value.columns)
        raise ValueError(f"Can't get columns for an empty dataset {value.unwrap_err()}.")
