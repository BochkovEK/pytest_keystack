# conftest.py
# Exchange variables between tests

import pytest


@pytest.hookimpl(optionalhook=True)
def pytest_namespace():
    return {
        'shared': None,
    }
