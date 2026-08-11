from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class StatePatch:
    """A partial experience-state change and the facets it supersedes."""

    values: dict
    changed_facets: tuple[str, ...]

    @classmethod
    def create(cls, values: dict, changed_facets: Iterable[str]) -> "StatePatch":
        if not isinstance(values, dict) or not values:
            raise ValueError("state patch must be a non-empty object")
        facets = tuple(dict.fromkeys(changed_facets))
        if not facets or any(not isinstance(item, str) or not item.strip() for item in facets):
            raise ValueError("changed facets must be non-empty strings")
        for facet in facets:
            value = values
            for segment in facet.split("."):
                if not isinstance(value, dict) or segment not in value:
                    raise ValueError(f"changed facet is absent from patch: {facet}")
                value = value[segment]
        return cls(values, facets)


def merge_state(current: dict, patch: dict) -> dict:
    """Apply object patches recursively without erasing sibling decisions."""

    if not isinstance(current, dict) or not isinstance(patch, dict):
        raise ValueError("experience state and patch must be objects")
    merged = dict(current)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_state(merged[key], value)
        else:
            merged[key] = value
    return merged
