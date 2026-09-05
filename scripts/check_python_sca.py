#!/usr/bin/env python3
"""Run the pinned pip-audit Python dependency SCA gate (#330)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from urllib.parse import quote
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".gitlab-ci.yml"
EXCEPTIONS = ROOT / "python-sca-exceptions.json"
PINNED_PACKAGE = "pip-audit==2.10.1"
FIXTURES = ROOT / "scripts" / "fixtures" / "sca"
KNOWN_BAD = FIXTURES / "known_bad.lock"
CLEAN_BASELINE = FIXTURES / "clean.lock"
LOCKS = (
    ROOT / "platform" / "requirements.lock",
    ROOT / "edge" / "requirements.lock",
)
REPORT = ROOT / "pip-audit-report.json"
OSV_VULN = "https://api.osv.dev/v1/vulns/{id}"
BLOCKING = frozenset({"HIGH", "CRITICAL"})
KNOWN_BAD_PACKAGE = "pyyaml"
KNOWN_BAD_VERSION = "5.3"
KNOWN_BAD_IDS = frozenset(
    {
        "GHSA-6757-jp84-gxfx",
        "CVE-2020-14343",
        "PYSEC-2020-143",
    }
)
OWNER_RE = re.compile(r"^@[a-z0-9][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LATER_SLICES = ("trivy", "checkov", "tfsec", "syft", "grype", "cosign")

OsvLookup = Callable[[str], dict[str, Any] | None]


def canonicalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def job_block(name: str) -> str:
    text = CI.read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(name)}:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError(f"{name} job missing from .gitlab-ci.yml")
    return match.group(0)


def find_pip_audit() -> str:
    binary = shutil.which("pip-audit")
    if not binary:
        print(
            f"FAIL: pip-audit is not on PATH. Install the pinned CLI: pip install {PINNED_PACKAGE}",
            file=sys.stderr,
        )
        sys.exit(2)
    return binary


def run_pip_audit(binary: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [binary, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def print_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)


def parse_lock_pins(lock: Path) -> list[tuple[str, str]]:
    pins: list[tuple[str, str]] = []
    for line in lock.read_text(encoding="utf-8").splitlines():
        stripped = line.split("#", 1)[0].strip()
        if not stripped:
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)==(.+)$", stripped)
        if not match:
            raise ValueError(f"unparseable lock line in {lock}: {line}")
        pins.append((canonicalize_name(match.group(1)), match.group(2).strip()))
    return pins


def load_exceptions() -> list[dict[str, str]]:
    if not EXCEPTIONS.is_file():
        print(f"FAIL: {EXCEPTIONS.relative_to(ROOT)} is missing", file=sys.stderr)
        sys.exit(1)
    try:
        payload = json.loads(EXCEPTIONS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: {EXCEPTIONS.name} is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(payload, dict) or not isinstance(payload.get("exceptions"), list):
        print(f"FAIL: {EXCEPTIONS.name} must be an object with an exceptions list", file=sys.stderr)
        sys.exit(1)
    parsed: list[dict[str, str]] = []
    for index, item in enumerate(payload["exceptions"]):
        if not isinstance(item, dict):
            print(f"FAIL: {EXCEPTIONS.name} exceptions[{index}] must be an object", file=sys.stderr)
            sys.exit(1)
        required = ("id", "package", "owner", "reason", "expires")
        missing = [key for key in required if not str(item.get(key, "")).strip()]
        if missing:
            print(
                f"FAIL: {EXCEPTIONS.name} exceptions[{index}] missing {', '.join(missing)}",
                file=sys.stderr,
            )
            sys.exit(1)
        owner = str(item["owner"]).strip()
        expires = str(item["expires"]).strip()
        if not OWNER_RE.match(owner):
            print(
                f"FAIL: {EXCEPTIONS.name} exceptions[{index}] owner must be @role ({owner!r})",
                file=sys.stderr,
            )
            sys.exit(1)
        if not DATE_RE.match(expires):
            print(
                f"FAIL: {EXCEPTIONS.name} exceptions[{index}] expires must be YYYY-MM-DD",
                file=sys.stderr,
            )
            sys.exit(1)
        parsed.append(
            {
                "id": str(item["id"]).strip(),
                "package": canonicalize_name(str(item["package"])),
                "owner": owner,
                "reason": str(item["reason"]).strip(),
                "expires": expires,
            }
        )
    return parsed


def exception_active(item: dict[str, str], today: date) -> bool:
    return date.fromisoformat(item["expires"]) >= today


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


def load_dependencies(payload: str) -> list[dict[str, Any]]:
    data = json.loads(payload)
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = data.get("dependencies", [])
    else:
        raise ValueError("pip-audit JSON must be a list or an object with dependencies")
    if not isinstance(rows, list):
        raise ValueError("pip-audit JSON dependencies must be a list")
    return [item for item in rows if isinstance(item, dict)]


def finding_ids(vuln: dict[str, Any]) -> set[str]:
    ids = {str(vuln.get("id", "")).strip()}
    aliases = vuln.get("aliases") or []
    if isinstance(aliases, list):
        ids.update(str(alias).strip() for alias in aliases)
    return {item for item in ids if item}


def collect_findings(dependencies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for item in dependencies:
        name = canonicalize_name(str(item.get("name") or ""))
        version = str(item.get("version") or "").strip()
        vulns = item.get("vulns") or []
        if not name or not isinstance(vulns, list):
            continue
        for vuln in vulns:
            if not isinstance(vuln, dict):
                continue
            vuln_id = str(vuln.get("id") or "").strip()
            if not vuln_id:
                continue
            fixes = vuln.get("fix_versions") or []
            findings.append(
                {
                    "package": name,
                    "version": version,
                    "id": vuln_id,
                    "aliases": sorted(finding_ids(vuln) - {vuln_id}),
                    "fix_versions": [str(fix) for fix in fixes] if isinstance(fixes, list) else [],
                    "description": str(vuln.get("description") or ""),
                }
            )
    return findings


def cvss_number(score: str) -> float | None:
    stripped = score.strip()
    if re.match(r"^\d+(?:\.\d+)?$", stripped):
        return float(stripped)
    match = re.search(r"/AV:", stripped)
    if not match:
        return None
    # Fail-closed qualitative read of a CVSS v3 vector: H impact on C/I/A
    # without a numeric score is treated as High, not parsed as a full CVSS lib.
    highs = len(re.findall(r"/[CIA]:H", stripped))
    if highs >= 2:
        return 9.0
    if highs == 1 or "/AC:L" in stripped:
        return 7.0
    return 4.0


def severity_from_osv(record: dict[str, Any] | None) -> str | None:
    if not record:
        return None
    specific = record.get("database_specific")
    if isinstance(specific, dict):
        raw = str(specific.get("severity") or "").strip().upper()
        if raw in {"LOW", "MEDIUM", "HIGH", "CRITICAL", "MODERATE"}:
            return "MEDIUM" if raw == "MODERATE" else raw
    rows = record.get("severity")
    if not isinstance(rows, list):
        return None
    best: float | None = None
    for item in rows:
        if not isinstance(item, dict):
            continue
        number = cvss_number(str(item.get("score") or ""))
        if number is None:
            continue
        best = number if best is None else max(best, number)
    if best is None:
        return None
    if best >= 9.0:
        return "CRITICAL"
    if best >= 7.0:
        return "HIGH"
    if best >= 4.0:
        return "MEDIUM"
    return "LOW"


def fetch_osv(vuln_id: str) -> dict[str, Any] | None:
    url = OSV_VULN.format(id=quote(vuln_id, safe=""))
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def classify_severity(finding: dict[str, Any], osv_lookup: OsvLookup) -> str:
    explicit = str(finding.get("severity") or "").strip().upper()
    if explicit in BLOCKING or explicit in {"LOW", "MEDIUM"}:
        return explicit
    for vuln_id in [finding["id"], *finding.get("aliases", [])]:
        mapped = severity_from_osv(osv_lookup(vuln_id))
        if mapped:
            return mapped
    return "HIGH"


def matching_exception(
    finding: dict[str, Any],
    exceptions: list[dict[str, str]],
    today: date,
) -> dict[str, str] | None:
    ids = {finding["id"], *finding.get("aliases", [])}
    for item in exceptions:
        if item["package"] != finding["package"]:
            continue
        if item["id"] not in ids:
            continue
        if not exception_active(item, today):
            continue
        return item
    return None


def blocking_findings(
    findings: list[dict[str, Any]],
    exceptions: list[dict[str, str]],
    osv_lookup: OsvLookup,
    today: date | None = None,
) -> list[dict[str, Any]]:
    when = today or today_utc()
    blocked: list[dict[str, Any]] = []
    for finding in findings:
        severity = classify_severity(finding, osv_lookup)
        finding["severity"] = severity
        if severity not in BLOCKING:
            continue
        if matching_exception(finding, exceptions, when):
            finding["accepted"] = True
            continue
        finding["accepted"] = False
        blocked.append(finding)
    return blocked


def summarize_blocking(findings: list[dict[str, Any]]) -> None:
    for item in findings:
        fixes = ",".join(item.get("fix_versions") or []) or "none"
        print(
            f"  {item['severity']} {item['id']} {item['package']}=={item['version']} fix={fixes}",
            file=sys.stderr,
        )


def write_report(dependencies: list[dict[str, Any]], findings: list[dict[str, Any]]) -> None:
    payload = {
        "dependencies": dependencies,
        "findings": findings,
        "blocking": [item for item in findings if item.get("severity") in BLOCKING and not item.get("accepted")],
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    REPORT.write_text(text, encoding="utf-8")
    print(f"ok: retained pip-audit report {REPORT.relative_to(ROOT)}")


def audit_lock(binary: str, lock: Path) -> tuple[list[dict[str, Any]], subprocess.CompletedProcess[str] | None]:
    if not lock.is_file():
        raise FileNotFoundError(f"missing lock: {lock}")
    pins = parse_lock_pins(lock)
    if not pins:
        return [], None
    result = run_pip_audit(
        binary,
        "-r",
        str(lock.relative_to(ROOT) if lock.is_relative_to(ROOT) else lock),
        "--format",
        "json",
        "--progress-spinner",
        "off",
        "--desc",
        "on",
    )
    print_output(result)
    if result.returncode not in {0, 1}:
        raise RuntimeError(f"pip-audit crashed on {lock}")
    stdout = result.stdout.strip() or "[]"
    return load_dependencies(stdout), result


def prove_known_bad(binary: str, osv_lookup: OsvLookup) -> int:
    dependencies, result = audit_lock(binary, KNOWN_BAD)
    findings = collect_findings(dependencies)
    blocked = blocking_findings(findings, [], osv_lookup)
    ids = set()
    for item in blocked:
        ids.update({item["id"], *item.get("aliases", [])})
    if not blocked or not (ids & KNOWN_BAD_IDS):
        print("FAIL: known-bad SCA fixture unexpectedly passed High/Critical", file=sys.stderr)
        return 0 if result is None or result.returncode == 0 else 1
    print(f"ok: known-bad SCA fixture failed as expected ({KNOWN_BAD_PACKAGE}=={KNOWN_BAD_VERSION})")
    return 1


def prove_clean_baseline() -> None:
    pins = parse_lock_pins(CLEAN_BASELINE)
    if pins:
        print("FAIL: clean SCA baseline must have no pins", file=sys.stderr)
        sys.exit(1)
    print("ok: clean SCA baseline passed")


def check_repository_locks(binary: str, exceptions: list[dict[str, str]], osv_lookup: OsvLookup) -> None:
    missing = [lock.relative_to(ROOT).as_posix() for lock in LOCKS if not lock.is_file()]
    if missing:
        print(f"FAIL: resolved Python locks missing: {missing}", file=sys.stderr)
        sys.exit(1)
    dependencies: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for lock in LOCKS:
        rows, _result = audit_lock(binary, lock)
        dependencies.extend(rows)
        findings.extend(collect_findings(rows))
    blocked = blocking_findings(findings, exceptions, osv_lookup)
    write_report(dependencies, findings)
    unused = unused_exceptions(findings, exceptions, today_utc())
    if unused:
        print("FAIL: unused or expired Python SCA exceptions", file=sys.stderr)
        for item in unused:
            print(f"  {item['id']} {item['package']} expires={item['expires']}", file=sys.stderr)
        sys.exit(1)
    if blocked:
        print("FAIL: unaccepted High/Critical Python dependency findings", file=sys.stderr)
        summarize_blocking(blocked)
        sys.exit(1)
    print(
        f"ok: platform and edge lock SCA exited 0 for High/Critical "
        f"({len(findings)} retained finding(s), 0 unaccepted High/Critical)"
    )


def unused_exceptions(
    findings: list[dict[str, Any]],
    exceptions: list[dict[str, str]],
    today: date,
) -> list[dict[str, str]]:
    unused: list[dict[str, str]] = []
    for item in exceptions:
        if not exception_active(item, today):
            unused.append(item)
            continue
        matched = False
        for finding in findings:
            ids = {finding["id"], *finding.get("aliases", [])}
            if item["package"] == finding["package"] and item["id"] in ids:
                matched = True
                break
        if not matched:
            unused.append(item)
    return unused


def ci_job_errors() -> list[str]:
    try:
        block = job_block("pip-audit")
        lock_block = job_block("python-lock")
    except AssertionError as exc:
        return [str(exc)]
    errors: list[str] = []
    if "allow_failure:" in block:
        errors.append("pip-audit must not set allow_failure")
    if "|| true" in block:
        errors.append("pip-audit must not suppress failures")
    if PINNED_PACKAGE not in block:
        errors.append(f"pip-audit must pin {PINNED_PACKAGE}")
    if "scripts/check_python_sca.py" not in block:
        errors.append("pip-audit must run scripts/check_python_sca.py")
    if "scripts/test_python_sca.py" not in block:
        errors.append("pip-audit must run scripts/test_python_sca.py")
    if "pip-audit-report.json" not in block:
        errors.append("pip-audit must retain pip-audit-report.json")
    if "when: always" not in block:
        errors.append("pip-audit must retain the report when: always")
    if any(token in block for token in LATER_SLICES):
        errors.append("pip-audit must not stack #331–#334 image/IaC scans")
    if "pip-audit" in lock_block or "osv-scanner" in lock_block or "safety check" in lock_block:
        errors.append("python-lock must not stack #330 dependency SCA")
    return errors


def check_ci_job() -> None:
    errors = ci_job_errors()
    if errors:
        print("FAIL: pip-audit CI job (#330)", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    print("ok: pip-audit CI job is required, pinned, and isolated from #331–#334")


def cached_osv_lookup() -> OsvLookup:
    cache: dict[str, dict[str, Any] | None] = {}

    def lookup(vuln_id: str) -> dict[str, Any] | None:
        if vuln_id not in cache:
            cache[vuln_id] = fetch_osv(vuln_id)
        return cache[vuln_id]

    return lookup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("all", "known-bad", "clean-baseline", "repo"),
        default="all",
    )
    args = parser.parse_args()
    exceptions = load_exceptions()
    check_ci_job()
    if args.mode == "clean-baseline":
        prove_clean_baseline()
        return 0
    binary = find_pip_audit()
    osv_lookup = cached_osv_lookup()
    if args.mode == "known-bad":
        result = prove_known_bad(binary, osv_lookup)
        return 1 if result == 0 else result
    if args.mode == "all":
        prove_clean_baseline()
        result = prove_known_bad(binary, osv_lookup)
        if result == 0:
            return 1
    if args.mode in {"all", "repo"}:
        check_repository_locks(binary, exceptions, osv_lookup)
    return 0


if __name__ == "__main__":
    sys.exit(main())
