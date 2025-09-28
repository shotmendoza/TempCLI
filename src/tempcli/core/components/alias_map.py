from collections import Counter
from collections.abc import Collection
from dataclasses import dataclass

import pandas as pd

from tempcli.core.components.data import DataSource
from tempcli.core.components.func import Fn
from tempcli.core.support.interfaces import FnResult
from tempcli.core.types.alias import One, Many, Alias
from tempcli.core.types.result import Result, Err, Ok


@dataclass(frozen=True)
class _RelevantAlias:
    """Stores the Alias values that are relevant to the current run.

    When `AliasMap` takes in DataSource and Fn as inputs, it searches
    for the Alias that is in both, the DataSource and Fn. This class
    stores those values and helps in converting the relevant aliases
    into a format that can be handled by BoundArguments class.

    Some functionality of this class includes:
        `sets`: a function that returns a usable set of alias arguments.

    First, the object normalizes the One and Many types, so that the arguments
    can be processed correctly as sets. The arguments are organized in a way
    to have a different combination, so that the input (a1, a2, a3), (b1, b2, b3)
    can be converted into (a1, b1), (a2, b2), and (a3, b3).

    """
    alias_collection: Collection[Alias]
    """used as a `hold` for the relevant aliases.
    this parameter will be used in creating the set we will use for the BoundArguments.
    """

    def sets(
            self,
            function: Fn,
            data_source: DataSource,
    ) -> Collection[FnResult]:
        """List of dictionary arguments, that represent arguments for BoundArguments.

        Used by Alias Map to normalize the relevant columns and function parameters.

        :param function: the function being called and referenced.
        :param data_source: the DataSource to use.
        :return: Collection[FnResult]
        """
        # === Normalize the Data for BoundArguments ===
        collection = self._normalized_collection()
        normalized_for_bound = [tuple(group) for group in zip(*collection)]

        # === Generate the BoundArgument format arguments ===
        args = []
        # Scalars
        if function.has_scalar_params:
            _column_alias_mapping = [{a.alias: a.parameter for a in g} for g in normalized_for_bound]
            for c in _column_alias_mapping:
                df: pd.DataFrame = data_source.data[c.keys()].copy().rename(columns=c)
                records = df.to_dict("records")
                args.append(records)

        # pd.Series
        else:
            df = data_source.data.copy()
            args = [{a.parameter: df[a.alias] for a in g} for g in normalized_for_bound]

        # === Run the Functions ===
        return self._apply_bound(function, args)

    @classmethod
    def _apply_bound(cls, function: Fn, args: list[dict]) -> Collection[FnResult]:
        """applies the bound arguments to the function and returns the results.

        Handles both the Scalar type of functions (int, str, etc.) and pd.Series type functions.
        Can consider this function normalizing both, the One-One and One-Many types of relationships
        as it relates to AliasMaps.

        :param function: the function being called and referenced.
        :param args: the list of arguments to pass to the function. We get this from _relevant_alias.sets().
        :return: Collection[FnResult]

        """
        results = []
        # Scalars
        if function.has_scalar_params:
            _args = []
            _kwargs = {}
            for arg in args:
                temp = [function.signature.bind_partial(**r) for r in arg]
                for t in temp:
                    t.apply_defaults()
                    temp_result: Result[FnResult, Exception] = function(*t.args, **t.kwargs)

                    # since fn() returns a FnResult, we need this step in order to make
                    # a pd.Series before wrapping the result into a FnResult
                    result: pd.Series = temp_result.unwrap().result
                    results.append(result)
            results = pd.Series(results)
            results = [FnResult(result=results, args=tuple(args[0].values()), kwargs=args[-1], fn_used=function.name)]

        # pd.Series
        else:
            for arg in args:
                bound_args = function.signature.bind_partial(**arg)
                bound_args.apply_defaults()
                result: Result[FnResult, Exception] = function(*bound_args.args, **bound_args.kwargs)
                results.append(result.unwrap_or(None))
        return results

    def _normalized_collection(self) -> Collection[Collection[Alias]]:
        """Normalizes the AliasMap collection by extrapolating the `One`
        object to match the length of the max `Many` object. Converts
        a `Many` object into a list of `One` objects. This collection
        can then be used to process the function arguments.

        :return: a list of a list, where the outer list holds a list for
        each parameter we are storing as an Alias object.
        """
        # Get the max Many size so the list of One can match its length
        _prev_max: str = "One"
        _max_size: int = 1
        for a in self.alias_collection:
            if isinstance(a, Many):
                if not _max_size:
                    _max_size = len(a.aliases)
                    _prev_max = a.parameter
                    continue
                if len(a.aliases) != _max_size:
                    msg = f"Columns of the alias_map must equal in size. Currently {_max_size}: {len(a.aliases)}. "
                    msg2 = f"Check {a.parameter} and {_prev_max}"
                    raise IndexError(msg + msg2)
                _max_size = max(_max_size, len(a.aliases))

        # Extrapolate the Ones and Convert Many to list of One
        normalized = []
        for a in self.alias_collection:
            if isinstance(a, Many):
                _into_ones = [ao for ao in a.convert_to_one()]
                normalized.append(_into_ones)
            elif isinstance(a, One):
                _extrapolated = a.extrapolate(num=_max_size)
                normalized.append(_extrapolated)
            else:
                raise TypeError(f"Unknown alias type: {type(a)}")
        return normalized


@dataclass
class AliasMap:
    """Represents an Alias Map, which is a user defined dictionary that maps
    out the parameter in the functions they want to use as the keys, and the
    name of the columns that tie to the report they are checking as the values.

        `config`: dict, the user defined mapping with param as the keys and column as the values.
        When one param has multiple associated columns, can be made into list `parameter` -> [c1, c2]
    """

    config: dict
    """The user input for the alias_map, or the mapping between function
    parameters and what the user expects the columns to be used for those
    parameters.
    """

    def __post_init__(self):
        # === Type Handling ===
        if not isinstance(self.config, dict):
            raise TypeError(f"`config` must be a dict. Got type {type(self.config)}.")

        if not self.config:
            raise ValueError("`config` must not be empty.")

        # === Dicts and Counters === [2025.09.27]
        # (1) I want a counter to see if we run into multiple same column names
        # (2) We can probably include a counter for param count for duplicates
        # we could even check for missing params
        self.p_count: Counter = Counter()
        """counter for parameters defined"""

        self.p: dict[str, Alias] = dict()
        """`parameter: Alias` dictionary"""

        self.c_count: Counter = Counter()
        """counter for columns defined"""

        self.c: dict[str, One] = dict()
        """`column: One` dictionary"""

        # iterating through the user written alias to initialize the dicts and counters
        for param, col in self.config.items():
            if isinstance(col, str):
                one = One(param, col)
                self.p[param] = one  # parameter as key
                self.p_count[param] += 1

                self.c[col] = one  # column as key
                self.c_count[col] += 1
                continue
            elif isinstance(col, Collection):
                many = Many(param, col)
                self.p[param] = many
                self.p_count[param] += 1

                self.c |= {m.alias: m for m in many.convert_to_one()}
                self.c_count |= {m.alias: 1 for m in many.convert_to_one()}
                continue
            else:
                raise TypeError(f"Unsupported type: {type(col)}")

    def check_params(
            self,
            params: Collection,
            raise_missing: bool = False,
    ) -> Result[Collection, Collection]:
        """needs a function that reads and returns Alias for
        given function parameters. Recommended to initialize the
        columns first, in case there are exact matches.

        :param params: the function parameters we are looking for, and to see if it was defined.
        :param raise_missing: whether to raise an exception if params are missing. False by default.
        This only applies to function related errors  and not errors for having bad types related to AliasMap.
        :return: a collection of matching params on Ok and empty collection on Err if `raise_missing` is False.
        """
        #################
        # Type Handling
        #################
        if not isinstance(params, Collection):
            raise TypeError(f"Columns must be a collection. Got {type(params)}")

        if isinstance(params, str):  # so the string doesn't get split
            params = [params]

        ##################
        # Logic
        ##################
        # [2025.09.27] will handle empty lists as an Err for now. Likely will
        # treat it with default values when we use BoundArgs
        if not params:
            if raise_missing:
                raise ValueError(f"Params must not be empty. Got {len(params)}")
            return Err([])

        # quick error if any of the params are missing from the alias_mapping
        missing_params = set(params) - set(self.p.keys())  # gets missing from left
        if missing_params:
            if raise_missing:
                raise KeyError(f"Missing expected parameters: {missing_params}.")
            return Err(missing_params)
        else:
            return Ok(params)

    def check_columns(
            self,
            columns: Collection,
            match_column: bool = True,
    ) -> Result[Collection, Collection]:
        """a function that finds the intersection for the alias and any column
        values that it is given.

        Will return a set of Alias that ties to the column if Ok, other an empty set if Err.

        :param columns: the columns we are looking to match with from a DataSource.
        :param match_column: flag to determine whether exact match column names should be included.
        This will look for columns that match the parameter names, even if not directly written by user.
        :return: a collection of matching columns on Ok and empty collection on Err
        """
        ##################
        # Error Handling
        ##################
        # ===Types===
        if not isinstance(columns, Collection):
            raise TypeError(f"Columns must be a collection. Got {type(columns)}")

        elif isinstance(columns, Collection) and isinstance(columns, str):
            raise TypeError(f"Columns cannot be a single string.")

        elif isinstance(columns, Collection) and isinstance(columns, pd.DataFrame):
            raise TypeError(f"Columns cannot be a single dataframe.")

        elif isinstance(columns, Collection) and isinstance(columns, pd.Series):
            raise TypeError(f"Columns cannot be a single series.")

        #################################
        # Match Columns to Alias Columns
        #################################
        # We can't match a DataFrame with no columns
        if len(columns) == 0:
            return Err(set())

        if match_column:
            matching_columns = set(columns) & set(self.p_count.keys())  # parameter exact with column
            for col in matching_columns:
                if not self.p_count.get(col):
                    one = One(col, col)
                    self.config[col] = one
                    self.p[col] = one
                    self.c[col] = one
                    self.p_count[col] += 1
                    self.c_count[col] += 1

        found = set(columns) & set(self.c.keys())  # match column to column
        if len(found) == 0:
            return Err(columns)
        return Ok(found)

    def generate_results(
            self,
            data: DataSource,
            fn: Fn,
            raise_missing: bool = False
    ) -> Result[Collection[FnResult], str]:
        """Takes the DataSource and Function, and returns a Collection[FnResult] if `Ok`
        If `raise_missing` if False, `Err` will return an error message. Otherwise, the
        function will raise the error message.

        The `Pipeline` or a manager that the `Pipeline` uses, will likely be the object
        using this function. Most likely, this function will be used as part of a loop,
        where the DataSource and Fn are being looped until all checks and reports are
        checked by the Pipeline.

        :param data: the DataSource being used for these functions and checks.
        :param fn: the function being used to check the reports.
        :param raise_missing: whether to raise an exception if a column is missing. Defaults to False.
        :return: a collection of FnResults[pd.Series] or an Error
        """
        # === Handling the DataSource Errors ===
        column_result = self.check_columns(columns=data.columns, match_column=True)
        if column_result.is_err:
            r = column_result.unwrap_err()
            msg = f"None of columns {r} matched, for fn `{fn.name}`. Add {fn.param_names} to `alias_map`."
            if raise_missing:
                raise KeyError(msg)
            return Err(msg)

        # === Handling the Function Errors ===
        fn_result = self.check_params(params=fn.param_names, raise_missing=raise_missing)
        if fn_result.is_err:
            r = fn_result.unwrap_err()
            msg = f"Missing columns {r} for data {data.name}. Please add it as `alias_map`."
            if raise_missing:
                raise KeyError(msg)
            return Err(msg)

        # === Handling the Relevant Aliases ===
        matched_params = [self.p[p] for p in fn_result.unwrap()]
        columns = column_result.unwrap()
        relevant_aliases = []
        for p in matched_params:
            result = p.map(columns)
            if isinstance(result, Ok):
                r = result.unwrap()
                relevant_aliases.append(r)

        # === Handling Normalization and Bound Args Creation ===
        normalized_alias = _RelevantAlias(relevant_aliases)
        results = normalized_alias.sets(function=fn, data_source=data)
        return Ok(results)
