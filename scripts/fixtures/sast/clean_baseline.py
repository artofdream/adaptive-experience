"""Clean Bandit baseline fixture.

A scoped-tree-shaped module that must produce zero High findings.
"""

VALUE = 1


def add(left: int, right: int) -> int:
    return left + right
