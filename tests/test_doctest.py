import doctest
from unittest import TestLoader, TestSuite

from indexme.db import file_model


def load_tests(loader: TestLoader, tests: TestSuite, pattern: str) -> TestSuite:
    tests.addTests(doctest.DocTestSuite(file_model))
    return tests
