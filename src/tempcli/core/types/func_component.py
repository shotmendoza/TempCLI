"""Module for typing unknown function parameters and return types"""
from dataclasses import dataclass

from typing_extensions import ParamSpec, TypeVar

P = ParamSpec("P")  # Param P
R = TypeVar("R")  # return R
