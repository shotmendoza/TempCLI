"""module for the manager object handling the orchestration of the 3 main components"""
from collections.abc import Collection

from tempcli.core.components.alias_map import AliasMap
from tempcli.core.components.data import DataSource
from tempcli.core.components.func import Fn
from tempcli.core.types.result import Ok, Err, Result


class PipeMixin:
    """object responsible for managing the 3 objects to complete the pipeline and checks.
    """
    @classmethod
    def run(
            cls,
            alias_map: AliasMap,
            data: DataSource,
            fn: Fn,
            raise_missing: bool = False
    ) -> Result:
        """

        :param alias_map:
        :param data:
        :param fn:
        :param raise_missing:
        :return:
        """
        result = alias_map.generate_results(data=data, fn=fn, raise_missing=raise_missing)
        if result.is_err():
            if raise_missing:
                raise result.unwrap_err()
            return result
        return Ok(result)


