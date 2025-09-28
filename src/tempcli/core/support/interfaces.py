from dataclasses import dataclass, field
from uuid import UUID, uuid5

import pandas as pd

from tempcli.config import TEMPCLI_NAMESPACE


@dataclass(frozen=True)
class FnResult:
    """object that holds the result of a function call.

    Creates a key when initialized to track the "run". This will allow to create an index based on the runs.

    Accepts the arguments on the initial init:
        `result`: [required] the result returned by the function. We want this to be a pd.Series ideally.

        `fn_used`: [required] the function used on the result. This is the name so str.

        `args`: [optional] the arguments passed to the function. We want this to be a tuple.

        `kwargs`: [optional] the keyword arguments passed to the function. We want this to be a dict.
    """
    result: pd.Series
    fn_used: str
    data_name: str = None
    args: tuple = None
    kwargs: dict = None

    _FN_RESULT_NAMESPACE: UUID = field(init=False)

    def __post_init__(self):
        # class UUID creation
        _FN_RESULT_NAMESPACE = uuid5(TEMPCLI_NAMESPACE, type(self).__name__)
        _gen_key = self._create_uuid(_FN_RESULT_NAMESPACE)

        # creating the run UUID
        object.__setattr__(
            self,
            'uuid',
            _gen_key
        )

    def _create_uuid(
            self,
            class_namespace: UUID
    ) -> UUID:
        """creates a unique UUID from the given data_name."""
        combined_s = []
        if self.args:
            a_s = "_".join(str(s) for s in self.args)
            combined_s.append(a_s)
        if self.kwargs:
            k_s = "_".join(f"{k}_{v}" for k, v in self.kwargs.items())
            combined_s.append(k_s)
        if self.data_name:
            combined_s.append(self.data_name)

        string_key = "|".join(str(c) for c in combined_s)
        return uuid5(class_namespace, string_key)
