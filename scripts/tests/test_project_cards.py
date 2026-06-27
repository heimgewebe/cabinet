from __future__ import annotations

import unittest

from test_project_cards_parser import ProjectCardParserTest
from test_project_cards_repository import RepositoryProjectCardsTest


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(ProjectCardParserTest))
    suite.addTests(loader.loadTestsFromTestCase(RepositoryProjectCardsTest))
    return suite


if __name__ == "__main__":
    unittest.main()
