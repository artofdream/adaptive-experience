"""Known-bad Ruff fixture.

This file must fail `ruff check` (F821). Do not add it to the scoped
repository baseline.
"""


def broken() -> object:
    return definitely_undefined_aea_327_name
