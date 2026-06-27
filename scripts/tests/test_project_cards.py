from __future__ import annotations

import unittest


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    return unittest.TestSuite()


if __name__ == "__main__":
    unittest.main()
