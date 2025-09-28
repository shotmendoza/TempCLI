import inspect
from collections.abc import Collection, Callable

import pandas as pd

from tempcli.core.components.alias_map import AliasMap
from tempcli.core.components.data import DataSource
from tempcli.core.components.func import Fn
from tempcli.core.support.manager import PipeMixin
from tempcli.core.types.result import Ok


class Pipeline(PipeMixin):
    def __init__(self, raise_errors:  bool = True):
        """Base Class for handling the Function validation. Will prep the function side of the equation
        so that no arise will come up when processing.

        1. Gets all the functions and their names
        2. Will grab the docstrings for the functions
        3. Will grab the function signatures
        """
        # === initialize map ===
        self.alias_map: AliasMap = self._initialize_aliases()
        self.data_sources: Collection[DataSource] = self._initialize_data_sources()
        self.functions: Collection[Fn] = self._initialize_functions()

    def _initialize_aliases(self) -> AliasMap:
        """goes down the inheritance chain and pulls the alias_map from each subclass.
        We centralize this data so that it can be used at any point in time.
        """
        # COMBINES ALL CLASS LEVELS OF ALIASES INTO ONE ALIAS
        # The idea is to take all the user defined alias_mapping from each subclass and make it into one dictionary
        aliases: dict | None = None
        for subclass in inspect.getmro(self.__class__)[:-1]:
            if "alias_map" in subclass.__dict__:
                temp = subclass.__dict__["alias_map"]  # holds the user-defined alias_mapping dict
                if aliases is None:
                    aliases = temp
                    continue
                # now I want to check to ensure we're not overriding values from the higher level classes
                override_param = {}
                for param, col in temp.items():
                    try:
                        aliases[param]  # check for keyword in dict
                    except KeyError:  # is a new parameter we want to add
                        override_param[param] = col
                aliases = aliases | override_param
        return AliasMap(aliases)

    def _initialize_data_sources(self) -> Collection[DataSource]:
        """goes down the inheritance chain and pulls the sources from each subclass."""
        _data_sources = list()
        acceptable_return_types = (pd.DataFrame, DataSource)
        for s_class in inspect.getmro(self.__class__)[:-1]:
            # (!) currently only looking for DataSources or DataFrames to turn into data sources
            for field, data in s_class.__dict__.items():
                if isinstance(data, DataSource):
                    _data_sources.append(data)
                    continue

                elif isinstance(data, pd.DataFrame):
                    ds = DataSource(field, data)
                    _data_sources.append(ds)
                    continue

                # Special case, but looks  for functions
                elif inspect.isfunction(data):
                    return_type = inspect.signature(data).return_annotation

                    # Returns a DataFrame
                    if return_type == acceptable_return_types[0]:
                        ds = DataSource(str(field), data())
                        _data_sources.append(ds)
                        continue

                    # Returns a  DataSource
                    elif return_type == acceptable_return_types[1]:
                        ds = data()
                        _data_sources.append(ds)
                        continue
        return _data_sources

    def _initialize_functions(self):
        """gets all functions defined by the user in the subclass. The list of functions then get split into those
        that are factories for the reports we are checking, and the checks that are being used when the pipeline
        is running.
        """
        # (1) Pulling all the functions under the class and subclass
        all_functions = list()
        for validation_class in inspect.getmro(self.__class__)[:-2]:
            for field, data in validation_class.__dict__.items():
                if isinstance(data, Callable) or isinstance(data, Fn):
                    # Given a Fn already for data
                    if isinstance(data, Callable) and not isinstance(data, Fn):
                        func = Fn(data)
                        all_functions.append(func)
                    elif isinstance(data, Fn):
                        all_functions.append(data)
        all_functions = list(set(all_functions))
        return all_functions

    def run_summary(self, raise_errors: bool = True) -> pd.DataFrame:

        results = {}
        for ds in self.data_sources:
            for f in self.functions:
                ds_id = ds.key
                f_id = f.key

                curr_result = self.run(
                    alias_map=self.alias_map,
                    data=ds,
                    fn=f,
                    raise_missing=raise_errors
                )

                if isinstance(curr_result, Ok):
                    r = curr_result.unwrap()
