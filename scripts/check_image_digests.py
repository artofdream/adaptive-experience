#!/usr/bin/env python3
"""Verify runtime/base and material CI/Compose images are digest-pinned (#331)."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".gitlab-ci.yml"
INVENTORY = ROOT / "research" / "random-thoughts" / "image-digest-pins.csv"
LEDGER = ROOT / "research" / "random-thoughts" / "dependency-pin-ledger.csv"
EXCEPTIONS = ROOT / "image-digest-exceptions.json"
REPORT = ROOT / "image-digest-report.json"
FIXTURES = ROOT / "scripts" / "fixtures" / "image-digests"
KNOWN_BAD_DOCKERFILE = FIXTURES / "unpinned.Dockerfile"
KNOWN_BAD_COMPOSE = FIXTURES / "unpinned-compose.yml"
CLEAN_DOCKERFILE = FIXTURES / "pinned.Dockerfile"

INVENTORY_HEADERS = ("image", "digest", "role", "evidence", "resolved")
MATERIAL_FILES = (
    ROOT / ".gitlab-ci.yml",
    ROOT / "platform" / "Dockerfile.orchestration",
    ROOT / "edge" / "bff" / "Dockerfile",
    ROOT / "edge" / "gateway" / "Dockerfile",
    ROOT / "platform" / "docker" / "Dockerfile.agent-runner",
    ROOT / "platform" / "docker" / "Dockerfile.grafana",
    ROOT / "platform" / "docker-compose.yml",
    ROOT / "edge" / "docker-compose.yml",
    ROOT / "edge" / "docker-compose.litellm.yml",
)
IMAGE_PREFIXES = (
    "python:",
    "cimg/android:",
    "docker:",
    "node:",
    "nginx:",
    "pgvector/pgvector:",
    "apache/kafka:",
    "grafana/grafana:",
    "ghcr.io/berriai/litellm:",
)
LATER_SLICES = ("trivy", "checkov", "tfsec", "syft", "grype", "cosign")
OWNER_RE = re.compile(r"^@[a-z0-9][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PINNED_RE = re.compile(r"^(.+?)@sha256:([0-9a-f]{64})$")
FROM_RE = re.compile(r"^\s*FROM\s+(\S+)", re.I)
IMAGE_RE = re.compile(r"^\s+image:\s+[\"']?(\S+?)[\"']?\s*(?:#.*)?$")
SERVICE_NAME_RE = re.compile(r"^\s+-\s+name:\s+[\"']?(\S+?)[\"']?\s*(?:#.*)?$")


def job_block(name: str) -> str:
    text = CI.read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(name)}:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError(f"{name} job missing from .gitlab-ci.yml")
    return match.group(0)


def looks_like_material_image(ref: str) -> bool:
    if ref.startswith("$") or ref.startswith("sha256:"):
        return False
    return any(ref.startswith(prefix) for prefix in IMAGE_PREFIXES)


def split_ref(ref: str) -> tuple[str, str | None]:
    match = PINNED_RE.match(ref)
    if match:
        return match.group(1), f"sha256:{match.group(2)}"
    return ref, None


def extract_refs(path: Path) -> list[str]:
    refs: list[str] = []
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    name = path.name
    dockerfile = (
        name == "Dockerfile"
        or name.startswith("Dockerfile.")
        or name.endswith(".Dockerfile")
    )
    for raw in text.splitlines():
        stripped = raw.split("#", 1)[0].rstrip()
        if not stripped.strip():
            continue
        ref = None
        if dockerfile:
            match = FROM_RE.match(stripped)
            if match:
                ref = match.group(1)
        else:
            match = IMAGE_RE.match(stripped) or SERVICE_NAME_RE.match(stripped)
            if match:
                ref = match.group(1)
        if ref and looks_like_material_image(ref):
            refs.append(ref)
    return refs


def load_inventory(path: Path = INVENTORY) -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise ValueError("image-digest-pins.csv missing")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(INVENTORY_HEADERS):
            raise ValueError("image-digest-pins.csv header mismatch")
        rows = list(reader)
    inventory: dict[str, dict[str, str]] = {}
    for row in rows:
        image = (row.get("image") or "").strip()
        digest = (row.get("digest") or "").strip()
        if not image or not DIGEST_RE.match(digest):
            raise ValueError(f"image-digest-pins.csv bad row: {row}")
        if image in inventory:
            raise ValueError(f"duplicate inventory image: {image}")
        inventory[image] = row
    if not inventory:
        raise ValueError("image-digest-pins.csv has no pin rows")
    return inventory


def load_exceptions(path: Path = EXCEPTIONS) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError("image-digest-exceptions.json missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("image-digest-exceptions.json must be a list")
    rows: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("exception rows must be objects")
        image = str(item.get("image") or "").strip()
        owner = str(item.get("owner") or "").strip()
        reason = str(item.get("reason") or "").strip()
        expires = str(item.get("expires") or "").strip()
        if not image or not OWNER_RE.match(owner) or not reason or not DATE_RE.match(expires):
            raise ValueError(f"exception needs image, @owner, reason, expires: {item}")
        rows.append({"image": image, "owner": owner, "reason": reason, "expires": expires})
    return rows


def matching_exception(image: str, exceptions: list[dict[str, Any]]) -> dict[str, Any] | None:
    for row in exceptions:
        if row["image"] == image:
            return row
    return None


def exception_errors(image: str, row: dict[str, Any], today: date | None = None) -> list[str]:
    today = today or date.today()
    errors: list[str] = []
    try:
        expiry = date.fromisoformat(str(row["expires"]))
    except ValueError:
        return [f"{image}: exception expires is not an ISO date"]
    if expiry < today:
        errors.append(f"{image}: exception expired on {row['expires']}")
    return errors


def collect_findings(
    files: list[Path],
    inventory: dict[str, dict[str, str]],
    exceptions: list[dict[str, Any]],
    today: date | None = None,
    *,
    enforce_coverage: bool = True,
) -> tuple[list[str], list[dict[str, Any]]]:
    today = today or date.today()
    errors: list[str] = []
    seen: list[dict[str, Any]] = []
    used_images: set[str] = set()
    used_exceptions: set[str] = set()
    for path in files:
        rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
        for ref in extract_refs(path):
            image, digest = split_ref(ref)
            used_images.add(image)
            exception = matching_exception(image, exceptions)
            if exception:
                used_exceptions.add(image)
                errors.extend(exception_errors(image, exception, today))
                if digest:
                    errors.append(f"{rel}: {image} is excepted and must not also carry a digest")
                seen.append({"file": rel, "image": image, "digest": None, "exception": True})
                continue
            if digest is None:
                errors.append(f"{rel}: {image} is not digest-pinned")
                continue
            pin = inventory.get(image)
            if pin is None:
                errors.append(f"{rel}: {image} digest is not recorded in image-digest-pins.csv")
                continue
            if pin["digest"] != digest:
                errors.append(
                    f"{rel}: {image} digest {digest} does not match inventory {pin['digest']}"
                )
                continue
            seen.append({"file": rel, "image": image, "digest": digest, "exception": False})
    if enforce_coverage:
        unused_inventory = sorted(set(inventory) - used_images)
        if unused_inventory:
            errors.append("unused inventory pins: " + ", ".join(unused_inventory))
        unused_exceptions = [row["image"] for row in exceptions if row["image"] not in used_exceptions]
        if unused_exceptions:
            errors.append("unused image-digest exceptions: " + ", ".join(unused_exceptions))
    return errors, seen


def fixture_unpinned_errors() -> list[str]:
    errors: list[str] = []
    for path in (KNOWN_BAD_DOCKERFILE, KNOWN_BAD_COMPOSE):
        refs = extract_refs(path)
        if not refs:
            errors.append(f"{path.name}: expected an unpinned material image")
            continue
        if any(split_ref(ref)[1] for ref in refs):
            errors.append(f"{path.name}: fixture must stay unpinned")
    return errors


def prove_known_bad() -> list[str]:
    inventory = load_inventory()
    errors, _seen = collect_findings(
        [KNOWN_BAD_DOCKERFILE, KNOWN_BAD_COMPOSE],
        inventory,
        [],
        enforce_coverage=False,
    )
    if not errors:
        return ["known-bad fixtures unexpectedly passed"]
    unpinned = [error for error in errors if "is not digest-pinned" in error]
    if len(unpinned) < 2:
        return ["known-bad fixtures must fail as unpinned images"]
    return []


def prove_clean_baseline() -> list[str]:
    inventory = load_inventory()
    errors, seen = collect_findings(
        [CLEAN_DOCKERFILE],
        inventory,
        [],
        enforce_coverage=False,
    )
    if errors:
        return errors
    if not seen:
        return ["clean fixture produced no pinned refs"]
    return []


def ledger_mentions_digest() -> list[str]:
    if not LEDGER.is_file():
        return ["dependency-pin-ledger.csv missing"]
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return ["dependency-pin-ledger.csv has no review rows"]
    last = rows[-1]
    blob = f"{last.get('dso_images', '')} {last.get('notes', '')}"
    if "#331" not in blob or "digest" not in blob.lower():
        return ["latest pin-cadence row must record #331 digest resolutions"]
    if "image-digest-pins.csv" not in blob:
        return ["latest pin-cadence row must point at image-digest-pins.csv"]
    return []


def ci_job_errors() -> list[str]:
    try:
        block = job_block("image-digest")
        sca_block = job_block("pip-audit")
    except AssertionError as exc:
        return [str(exc)]
    errors: list[str] = []
    if "allow_failure:" in block:
        errors.append("image-digest must not set allow_failure")
    if "|| true" in block:
        errors.append("image-digest must not suppress failures")
    if "scripts/check_image_digests.py" not in block:
        errors.append("image-digest must run scripts/check_image_digests.py")
    if "scripts/test_image_digests.py" not in block:
        errors.append("image-digest must run scripts/test_image_digests.py")
    if "image-digest-report.json" not in block:
        errors.append("image-digest must retain image-digest-report.json")
    if "when: always" not in block:
        errors.append("image-digest must retain the report when: always")
    if any(token in block for token in LATER_SLICES):
        errors.append("image-digest must not stack #332/#334 image/IaC scans")
    if "image-digest" in sca_block or any(token in sca_block for token in LATER_SLICES if token in ("trivy", "syft")):
        if "image-digest" in sca_block:
            errors.append("pip-audit must not stack #331 image digest pinning")
    return errors


def write_report(seen: list[dict[str, Any]], errors: list[str]) -> None:
    payload = {
        "issue": 331,
        "ok": not errors,
        "pins": seen,
        "errors": errors,
    }
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("all", "known-bad", "clean-baseline", "repo"),
        default="all",
    )
    args = parser.parse_args(argv)
    errors = ci_job_errors()
    if args.mode in {"all", "known-bad"}:
        errors.extend(prove_known_bad() if args.mode == "known-bad" else [])
        if args.mode == "known-bad":
            known = prove_known_bad()
            if known:
                print("FAIL: image digest gate (#331)", file=sys.stderr)
                for error in known:
                    print(f"  - {error}", file=sys.stderr)
                return 1
            print("ok: known-bad unpinned fixtures fail the image digest gate")
            return 0
    if args.mode in {"all", "clean-baseline"}:
        errors.extend(prove_clean_baseline())
    if args.mode == "all":
        known = prove_known_bad()
        if known:
            errors.extend(known)
    if args.mode in {"all", "repo"}:
        try:
            inventory = load_inventory()
            exceptions = load_exceptions()
        except ValueError as exc:
            errors.append(str(exc))
            inventory = {}
            exceptions = []
        repo_errors, seen = collect_findings(list(MATERIAL_FILES), inventory, exceptions)
        errors.extend(repo_errors)
        errors.extend(ledger_mentions_digest())
        write_report(seen, errors)
    else:
        write_report([], errors)
    if errors:
        print("FAIL: image digest gate (#331)", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("ok: runtime/base and material CI/Compose images are digest-pinned")
    print(f"ok: retained image digest report {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
