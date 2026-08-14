#!/usr/bin/env python3
"""Validate MVP topic contracts and JSON Schemas (ADR-008 / #129).

The generator's TOPICS inventory is the reviewed machine-readable payload
manifest. This guard reconciles that manifest with topic-contracts.md and the
schema files, then applies identity, envelope, and compatibility rules.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from write_mvp_topic_schemas import TOPICS

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "docs" / "04-technical-architecture" / "topic-contracts.md"
SCHEMAS = ROOT / "docs" / "04-technical-architecture" / "schemas"

DIALECT = "https://json-schema.org/draft/2020-12/schema"
SCHEMA_BASE = (
    "https://gitlab.com/artof-group/adaptive-experience-architecture/"
    "-/blob/main/docs/04-technical-architecture/schemas/"
)
ENVELOPE_NAME = "message-envelope.v1.0.0.json"
ENVELOPE_TITLE = "adaptive-experience.message-envelope"
ENVELOPE_REQUIRED = {
    "message_id",
    "topic",
    "message_type",
    "schema_version",
    "session_id",
    "correlation_id",
    "source",
    "context_version",
    "publication_time",
    "security_context",
    "payload",
    "outcome",
}

ROW = re.compile(
    r"^\|\s*([a-z0-9_.]+)\s*\|\s*([0-9]+\.[0-9]+\.[0-9]+)\s*\|",
    re.MULTILINE,
)
PAYLOAD_FILE = re.compile(
    r"^(?P<topic>[a-z0-9_.]+)\.v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)\.json$"
)
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def mvp_topics(path: Path = CONTRACTS) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    cut = text.find("## Future topics")
    body = text if cut < 0 else text[:cut]
    return [(match.group(1), match.group(2)) for match in ROW.finditer(body)]


def manifest() -> dict[tuple[str, str], tuple[dict[str, Any], list[str]]]:
    return {
        (topic, version): (properties, required)
        for topic, version, properties, required in TOPICS
    }


def schema_name(topic: str, version: str) -> str:
    return f"{topic}.v{version}.json"


def load_schema(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: invalid JSON: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{path.name}: schema document must be an object")
        return None
    return data


def validate_identity(
    name: str,
    data: dict[str, Any],
    title: str,
    errors: list[str],
) -> None:
    expected_id = SCHEMA_BASE + name
    if data.get("$schema") != DIALECT:
        errors.append(f"{name}: $schema must be {DIALECT}")
    if data.get("$id") != expected_id:
        errors.append(f"{name}: $id must be {expected_id}")
    if data.get("title") != title:
        errors.append(f"{name}: title must be {title}")
    if data.get("type") != "object":
        errors.append(f"{name}: root type must be object")
    if data.get("additionalProperties") is not False:
        errors.append(f"{name}: additionalProperties must be false")


def validate_payload(
    topic: str,
    version: str,
    data: dict[str, Any],
    expected_properties: dict[str, Any],
    expected_required: list[str],
    errors: list[str],
) -> None:
    name = schema_name(topic, version)
    validate_identity(name, data, topic, errors)
    properties = data.get("properties")
    required = data.get("required")
    if properties != expected_properties:
        errors.append(f"{name}: properties differ from the reviewed minimum payload")
    if required != expected_required:
        errors.append(f"{name}: required fields differ from the reviewed minimum payload")
    if not isinstance(required, list) or len(required) != len(set(required)):
        errors.append(f"{name}: required must be a duplicate-free list")
    if isinstance(properties, dict) and isinstance(required, list):
        unknown = sorted(set(required) - set(properties))
        if unknown:
            errors.append(f"{name}: required fields missing from properties: {unknown}")


def validate_envelope(data: dict[str, Any], errors: list[str]) -> None:
    validate_identity(ENVELOPE_NAME, data, ENVELOPE_TITLE, errors)
    properties = data.get("properties")
    required = data.get("required")
    if not isinstance(properties, dict):
        errors.append(f"{ENVELOPE_NAME}: properties must be an object")
        return
    if set(properties) != ENVELOPE_REQUIRED:
        errors.append(
            f"{ENVELOPE_NAME}: properties must be the ADR-008 envelope inventory"
        )
    if not isinstance(required, list) or set(required) != ENVELOPE_REQUIRED:
        errors.append(
            f"{ENVELOPE_NAME}: required must contain every ADR-008 envelope field"
        )
    message_type = properties.get("message_type", {})
    if message_type.get("enum") != ["event", "command", "query", "response"]:
        errors.append(f"{ENVELOPE_NAME}: message_type enum is invalid")
    schema_version = properties.get("schema_version", {})
    if schema_version.get("pattern") != r"^[0-9]+\.[0-9]+\.[0-9]+$":
        errors.append(f"{ENVELOPE_NAME}: schema_version must enforce semantic versioning")


def version_tuple(version: str) -> tuple[int, int, int]:
    if not SEMVER.fullmatch(version):
        raise ValueError(version)
    return tuple(int(part) for part in version.split("."))  # type: ignore[return-value]


def compatibility_errors(
    topic: str, versions: list[tuple[str, dict[str, Any]]]
) -> list[str]:
    """Return breaking same-major changes among schema versions in the tree."""
    errors: list[str] = []
    ordered = sorted(versions, key=lambda item: version_tuple(item[0]))
    for (old_version, old), (new_version, new) in zip(ordered, ordered[1:]):
        if version_tuple(old_version)[0] != version_tuple(new_version)[0]:
            continue
        old_props = old.get("properties", {})
        new_props = new.get("properties", {})
        removed = sorted(set(old_props) - set(new_props))
        changed = sorted(
            field
            for field in set(old_props) & set(new_props)
            if old_props[field] != new_props[field]
        )
        added_required = sorted(set(new.get("required", [])) - set(old.get("required", [])))
        prefix = f"{topic} {old_version}->{new_version}"
        if removed:
            errors.append(f"{prefix}: same-major version removes properties {removed}")
        if changed:
            errors.append(f"{prefix}: same-major version changes properties {changed}")
        if added_required:
            errors.append(
                f"{prefix}: same-major version adds required fields {added_required}"
            )
    return errors


def validate_inventory(
    contract_topics: list[tuple[str, str]],
    schemas: Path,
    payload_manifest: dict[tuple[str, str], tuple[dict[str, Any], list[str]]],
) -> list[str]:
    errors: list[str] = []
    expected = len(payload_manifest)
    if len(contract_topics) != expected or len(set(contract_topics)) != expected:
        errors.append(
            f"topic-contracts.md must contain exactly {expected} unique governed topics; "
            f"found {len(contract_topics)}"
        )
    if set(contract_topics) != set(payload_manifest):
        errors.append("topic-contracts.md and the generator payload manifest differ")

    json_files = sorted(schemas.glob("*.json"))
    envelope_path = schemas / ENVELOPE_NAME
    if not envelope_path.is_file():
        errors.append(f"missing envelope schema {ENVELOPE_NAME}")
    else:
        envelope = load_schema(envelope_path, errors)
        if envelope is not None:
            validate_envelope(envelope, errors)

    known_topics = {topic for topic, _ in contract_topics}
    active = set(contract_topics)
    found_active: set[tuple[str, str]] = set()
    historical: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)

    for path in json_files:
        if path.name == ENVELOPE_NAME:
            continue
        match = PAYLOAD_FILE.fullmatch(path.name)
        if match is None:
            errors.append(f"unexpected or misnamed schema file {path.name}")
            continue
        topic, version = match.group("topic"), match.group("version")
        if topic not in known_topics:
            errors.append(f"{path.name}: topic is not in the governed topic registry")
            continue
        data = load_schema(path, errors)
        if data is None:
            continue
        validate_identity(path.name, data, topic, errors)
        historical[topic].append((version, data))
        key = (topic, version)
        if key in active:
            found_active.add(key)
            expected_properties, expected_required = payload_manifest[key]
            validate_payload(
                topic,
                version,
                data,
                expected_properties,
                expected_required,
                errors,
            )

    missing = sorted(active - found_active)
    for topic, version in missing:
        errors.append(f"missing active schema {schema_name(topic, version)}")
    for topic, versions in historical.items():
        errors.extend(compatibility_errors(topic, versions))
    return errors


def main() -> int:
    errors = validate_inventory(mvp_topics(), SCHEMAS, manifest())
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"ok: {len(mvp_topics())} governed payload schemas, envelope, identity, "
        "minimum payload, and compatibility rules pass"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
