import pytest

from conftest import PIPE_MIXIN_STANDARD_TEST_CASES
from tempcli.core.support.manager import PipeMixin


@pytest.mark.parametrize("alias_map, data, f1, f2, err", PIPE_MIXIN_STANDARD_TEST_CASES)
def test_pipe(alias_map, data, f1, f2, err):
    if err == KeyError:
        with pytest.raises(err):
            p1 = PipeMixin.run(alias_map=alias_map, data=data, fn=f1, raise_missing=True)
            p2 = PipeMixin.run(alias_map=alias_map, data=data, fn=f2, raise_missing=True)
    else:
        p1 = PipeMixin.run(alias_map=alias_map, data=data, fn=f1, raise_missing=True)
        p2 = PipeMixin.run(alias_map=alias_map, data=data, fn=f2, raise_missing=True)
        assert p1.unwrap().is_ok()
        assert p2.unwrap().is_ok()
