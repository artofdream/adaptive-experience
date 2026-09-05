#!/usr/bin/env python3
"""Validate Terraform and scan IaC for world-open non-ALB ingress (#334)."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".gitlab-ci.yml"
STACK = ROOT / "infra" / "aws"
EXCEPTIONS = ROOT / "iac-scan-exceptions.json"
REPORT = ROOT / "iac-scan-report.json"
FIXTURES = ROOT / "scripts" / "fixtures" / "iac-scan"
KNOWN_BAD = FIXTURES / "known-bad"
CLEAN = FIXTURES / "clean"
PINNED_TERRAFORM = "1.9.8"
PINNED_CHECKOV = "3.2.447"
PINNED_CHECKOV_PKG = f"checkov=={PINNED_CHECKOV}"
TF_RELEASE = f"https://releases.hashicorp.com/terraform/{PINNED_TERRAFORM}"
OWNER_RE = re.compile(r"^@[a-z0-9][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RESOURCE_START = re.compile(
    r'^resource\s+"(?P<rtype>aws_security_group|aws_security_group_rule|'
    r'aws_vpc_security_group_ingress_rule)"\s+"(?P<name>[^"]+)"\s*\{',
    re.M,
)
VARIABLE_START = re.compile(r'^variable\s+"(?P<name>[^"]+)"\s*\{', re.M)
NESTED_START = re.compile(r"^\s*(ingress|egress)\s*\{", re.M)
WORLD_OPEN = frozenset({"0.0.0.0/0", "::/0"})
ALB_NAMES = frozenset({"alb"})
BLOCKING_CHECKOV = frozenset(
    {
        "CKV_AWS_24",
        "CKV_AWS_25",
        "CKV_AWS_260",
        "AVD-AWS-0107",
        "CKV_AWS_107",
    }
)
WORLD_OPEN_ID = "WORLD_OPEN_NON_ALB"
LATER_SLICES = ("syft", "grype", "cosign")
AWS_ENV = (
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_PROFILE",
    "AWS_WEB_IDENTITY_TOKEN_FILE",
)


def job_block(name: str) -> str:
    text = CI.read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(name)}:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError(f"{name} job missing from .gitlab-ci.yml")
    return match.group(0)


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


def strip_line_comments(text: str) -> str:
    lines = []
    for raw in text.splitlines():
        if raw.lstrip().startswith("#"):
            continue
        if " #" in raw:
            raw = raw.split(" #", 1)[0]
        lines.append(raw)
    return "\n".join(lines)


def extract_brace_block(text: str, open_at: int) -> tuple[str, int]:
    depth = 0
    for index in range(open_at, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_at + 1 : index], index + 1
    raise ValueError("unbalanced HCL brace block")


def iter_resource_blocks(text: str) -> list[dict[str, str]]:
    cleaned = strip_line_comments(text)
    blocks: list[dict[str, str]] = []
    for match in RESOURCE_START.finditer(cleaned):
        body, _end = extract_brace_block(cleaned, match.end() - 1)
        blocks.append(
            {
                "type": match.group("rtype"),
                "name": match.group("name"),
                "body": body,
                "address": f"{match.group('rtype')}.{match.group('name')}",
            }
        )
    return blocks


def iter_nested(body: str, kind: str) -> list[str]:
    blocks: list[str] = []
    for match in NESTED_START.finditer(body):
        if match.group(1) != kind:
            continue
        nested, _end = extract_brace_block(body, match.end() - 1)
        blocks.append(nested)
    return blocks


def world_open_vars(text: str) -> set[str]:
    cleaned = strip_line_comments(text)
    found: set[str] = set()
    for match in VARIABLE_START.finditer(cleaned):
        body, _end = extract_brace_block(cleaned, match.end() - 1)
        if any(token in body for token in WORLD_OPEN):
            found.add(match.group("name"))
    return found


def cidr_is_world_open(value: str, variables: set[str]) -> bool:
    if any(token in value for token in WORLD_OPEN):
        return True
    for name in variables:
        if re.search(rf"\bvar\.{re.escape(name)}\b", value):
            return True
    return False


def is_alb_resource(name: str, body: str = "") -> bool:
    if name in ALB_NAMES or name.endswith("_alb") or name.startswith("alb_"):
        return True
    if re.search(r"\baws_security_group\.alb\b", body):
        return True
    return False


def ingress_is_world_open(body: str, variables: set[str]) -> bool:
    assignments = re.findall(
        r"(?:cidr_blocks|ipv6_cidr_blocks|cidr_ipv4|cidr_ipv6)\s*=\s*([^\n]+)",
        body,
    )
    return any(cidr_is_world_open(item, variables) for item in assignments)


def collect_world_open(paths: list[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    sources: list[tuple[Path, str]] = []
    combined_vars: set[str] = set()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        sources.append((path, text))
        combined_vars.update(world_open_vars(text))
    for path, text in sources:
        rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
        for resource in iter_resource_blocks(text):
            rtype = resource["type"]
            name = resource["name"]
            body = resource["body"]
            alb = is_alb_resource(name, body)
            suspects: list[str] = []
            if rtype == "aws_security_group":
                suspects.extend(iter_nested(body, "ingress"))
            elif rtype == "aws_security_group_rule":
                if re.search(r'type\s*=\s*"ingress"', body):
                    suspects.append(body)
            else:
                suspects.append(body)
            if not any(ingress_is_world_open(item, combined_vars) for item in suspects):
                continue
            if alb:
                continue
            findings.append(
                {
                    "id": WORLD_OPEN_ID,
                    "resource": resource["address"],
                    "file": rel,
                    "severity": "HIGH",
                    "aliases": [],
                    "check": "world-open non-ALB ingress",
                }
            )
    return findings


def terraform_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.rglob("*.tf") if path.is_file())


def load_exceptions(path: Path = EXCEPTIONS) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError("iac-scan-exceptions.json missing")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("exceptions"), list):
        raise ValueError("iac-scan-exceptions.json must be an object with an exceptions list")
    parsed: list[dict[str, str]] = []
    for index, item in enumerate(payload["exceptions"]):
        if not isinstance(item, dict):
            raise ValueError(f"exceptions[{index}] must be an object")
        required = ("id", "resource", "owner", "reason", "expires")
        missing = [key for key in required if not str(item.get(key, "")).strip()]
        if missing:
            raise ValueError(f"exceptions[{index}] missing {', '.join(missing)}")
        owner = str(item["owner"]).strip()
        expires = str(item["expires"]).strip()
        if not OWNER_RE.match(owner):
            raise ValueError(f"exceptions[{index}] owner must be @role ({owner!r})")
        if not DATE_RE.match(expires):
            raise ValueError(f"exceptions[{index}] expires must be YYYY-MM-DD")
        parsed.append(
            {
                "id": str(item["id"]).strip(),
                "resource": str(item["resource"]).strip(),
                "owner": owner,
                "reason": str(item["reason"]).strip(),
                "expires": expires,
            }
        )
    return parsed


def exception_active(item: dict[str, str], today: date) -> bool:
    return date.fromisoformat(item["expires"]) >= today


def matching_exception(
    finding: dict[str, Any],
    exceptions: list[dict[str, str]],
    today: date,
) -> dict[str, str] | None:
    ids = {str(finding.get("id") or ""), *finding.get("aliases", [])}
    for item in exceptions:
        if not exception_active(item, today):
            continue
        if item["id"] not in ids:
            continue
        if item["resource"] not in {"*", finding.get("resource")}:
            continue
        return item
    return None


def blocking_findings(
    findings: list[dict[str, Any]],
    exceptions: list[dict[str, str]],
    today: date | None = None,
) -> list[dict[str, Any]]:
    when = today or today_utc()
    blocked: list[dict[str, Any]] = []
    for finding in findings:
        severity = str(finding.get("severity") or "HIGH").upper()
        finding["severity"] = severity
        check_id = str(finding.get("id") or "")
        is_world_open = check_id == WORLD_OPEN_ID
        is_checkov_block = check_id in BLOCKING_CHECKOV
        if not is_world_open and not is_checkov_block:
            finding["accepted"] = False
            continue
        if matching_exception(finding, exceptions, when):
            finding["accepted"] = True
            continue
        finding["accepted"] = False
        blocked.append(finding)
    return blocked


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
            ids = {str(finding.get("id") or ""), *finding.get("aliases", [])}
            if item["id"] not in ids:
                continue
            if item["resource"] not in {"*", finding.get("resource")}:
                continue
            matched = True
            break
        if not matched:
            unused.append(item)
    return unused


def load_checkov_report(payload: str | Path) -> dict[str, Any]:
    if isinstance(payload, Path):
        text = payload.read_text(encoding="utf-8")
    else:
        text = payload
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("checkov JSON must be an object")
    return data


def collect_checkov_findings(report: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    results = report.get("results") or {}
    failed = results.get("failed_checks") if isinstance(results, dict) else None
    if not isinstance(failed, list):
        failed = report.get("failed_checks") if isinstance(report.get("failed_checks"), list) else []
    for item in failed:
        if not isinstance(item, dict):
            continue
        check_id = str(item.get("check_id") or "").strip()
        if not check_id:
            continue
        aliases = []
        for key in ("bc_check_id", "guideline"):
            value = str(item.get(key) or "").strip()
            if value and value != check_id and value.startswith(("CKV_", "AVD-")):
                aliases.append(value)
        findings.append(
            {
                "id": check_id,
                "aliases": aliases,
                "resource": str(item.get("resource") or "").strip(),
                "file": str(item.get("file_path") or item.get("repo_file_path") or "").strip(),
                "severity": str(item.get("severity") or "HIGH").strip().upper(),
                "check": str(item.get("check_name") or "").strip(),
            }
        )
    return findings


def prove_known_bad() -> list[str]:
    paths = terraform_files(KNOWN_BAD)
    if not paths:
        return ["known-bad IaC fixture is missing"]
    findings = collect_world_open(paths)
    blocked = blocking_findings(findings, [])
    if not blocked or not any(item["id"] == WORLD_OPEN_ID for item in blocked):
        return ["known-bad world-open non-ALB fixture unexpectedly passed"]
    if any("alb" in item["resource"] for item in blocked):
        return ["known-bad fixture must fail a non-ALB resource"]
    return []


def prove_clean_baseline() -> list[str]:
    paths = terraform_files(CLEAN)
    if not paths:
        return ["clean IaC fixture is missing"]
    findings = collect_world_open(paths)
    blocked = blocking_findings(findings, [])
    if blocked:
        return ["clean IaC fixture produced blocking world-open non-ALB findings"]
    return []


def ci_job_errors() -> list[str]:
    try:
        block = job_block("iac-scan")
        scan_block = job_block("image-scan")
    except AssertionError as exc:
        return [str(exc)]
    errors: list[str] = []
    if "allow_failure:" in block:
        errors.append("iac-scan must not set allow_failure")
    if "|| true" in block:
        errors.append("iac-scan must not suppress failures")
    if PINNED_TERRAFORM not in block and "--install-terraform" not in block:
        errors.append(f"iac-scan must pin Terraform {PINNED_TERRAFORM}")
    if PINNED_CHECKOV_PKG not in block:
        errors.append(f"iac-scan must pin {PINNED_CHECKOV_PKG}")
    if "scripts/check_iac_scan.py" not in block:
        errors.append("iac-scan must run scripts/check_iac_scan.py")
    if "scripts/test_iac_scan.py" not in block:
        errors.append("iac-scan must run scripts/test_iac_scan.py")
    if "--install-terraform" not in block:
        errors.append("iac-scan must install the pinned Terraform release")
    if "iac-scan-report.json" not in block:
        errors.append("iac-scan must retain iac-scan-report.json")
    if "when: always" not in block:
        errors.append("iac-scan must retain the report when: always")
    if "AWS_ACCESS_KEY_ID" in block or "AWS_SECRET_ACCESS_KEY" in block:
        errors.append("iac-scan must not require AWS credentials")
    if any(token in block for token in LATER_SLICES):
        errors.append("iac-scan must not stack later SBOM/signing slices")
    if "checkov" in scan_block or "tfsec" in scan_block or "terraform fmt" in scan_block:
        errors.append("image-scan must not stack #334 IaC scans")
    return errors


def write_report(
    findings: list[dict[str, Any]],
    errors: list[str],
    extra: dict[str, Any] | None = None,
) -> None:
    payload = {
        "issue": 334,
        "ok": not errors,
        "terraform": PINNED_TERRAFORM,
        "checkov": PINNED_CHECKOV,
        "findings": findings,
        "blocking": [
            item
            for item in findings
            if not item.get("accepted")
            and (item.get("id") == WORLD_OPEN_ID or item.get("id") in BLOCKING_CHECKOV)
        ],
        "errors": errors,
    }
    if extra:
        payload.update(extra)
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"ok: retained IaC scan report {REPORT.relative_to(ROOT)}")


def run_cmd(args: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(args, cwd=cwd or ROOT, check=False, capture_output=True, text=True, env=merged)


def print_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)


def find_terraform() -> str:
    binary = shutil.which("terraform")
    if not binary:
        print(
            f"FAIL: terraform is not on PATH. Install the pinned release {PINNED_TERRAFORM} "
            "(python3 scripts/check_iac_scan.py --install-terraform)",
            file=sys.stderr,
        )
        sys.exit(2)
    return binary


def find_checkov() -> str:
    binary = shutil.which("checkov")
    if not binary:
        print(
            f"FAIL: checkov is not on PATH. Install the pinned CLI: pip install {PINNED_CHECKOV_PKG}",
            file=sys.stderr,
        )
        sys.exit(2)
    return binary


def terraform_version(binary: str) -> str:
    result = run_cmd([binary, "version", "-json"])
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {}
    return str(payload.get("terraform_version") or "")


def checkov_version(binary: str) -> str:
    result = run_cmd([binary, "--version"])
    blob = f"{result.stdout}\n{result.stderr}"
    match = re.search(r"(\d+\.\d+\.\d+)", blob)
    return match.group(1) if match else ""


def require_live_tools() -> tuple[str, str]:
    terraform = find_terraform()
    version = terraform_version(terraform)
    if version != PINNED_TERRAFORM:
        print(
            f"FAIL: terraform {version or 'unknown'} is not the pinned release {PINNED_TERRAFORM}",
            file=sys.stderr,
        )
        sys.exit(2)
    checkov = find_checkov()
    ck_version = checkov_version(checkov)
    if ck_version != PINNED_CHECKOV:
        print(
            f"FAIL: checkov {ck_version or 'unknown'} is not the pinned release {PINNED_CHECKOV}",
            file=sys.stderr,
        )
        sys.exit(2)
    return terraform, checkov


def tf_asset() -> str:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        arch = "amd64"
    elif machine in {"aarch64", "arm64"}:
        arch = "arm64"
    else:
        raise RuntimeError(f"unsupported machine for Terraform pin: {machine}")
    return f"terraform_{PINNED_TERRAFORM}_linux_{arch}.zip"


def download(url: str, dest: Path) -> None:
    curl = shutil.which("curl")
    if curl:
        result = run_cmd([curl, "-fsSL", "-o", str(dest), url])
        if result.returncode == 0 and dest.is_file() and dest.stat().st_size > 0:
            return
        print_output(result)
    try:
        import urllib.request

        request = urllib.request.Request(url, headers={"User-Agent": "aea-iac-scan"})
        with urllib.request.urlopen(request, timeout=60) as response:
            dest.write_bytes(response.read())
    except (OSError, TimeoutError) as exc:
        raise RuntimeError(f"download failed: {url}") from exc
    if not dest.is_file() or dest.stat().st_size == 0:
        raise RuntimeError(f"download failed: {url}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_sha256(checksums: str, filename: str) -> str:
    for raw in checksums.splitlines():
        parts = raw.split()
        if len(parts) >= 2 and parts[-1].lstrip("*") == filename:
            return parts[0].lower()
    raise ValueError(f"{filename} missing from Terraform checksums")


def install_terraform(dest_dir: Path | None = None) -> int:
    dest = dest_dir or Path(os.environ.get("TERRAFORM_INSTALL_DIR", "/usr/local/bin"))
    dest.mkdir(parents=True, exist_ok=True)
    asset = tf_asset()
    try:
        with tempfile.TemporaryDirectory(prefix="terraform-pin-") as tmp:
            tmpdir = Path(tmp)
            archive = tmpdir / asset
            checksums = tmpdir / f"terraform_{PINNED_TERRAFORM}_SHA256SUMS"
            download(f"{TF_RELEASE}/{asset}", archive)
            download(f"{TF_RELEASE}/terraform_{PINNED_TERRAFORM}_SHA256SUMS", checksums)
            expected = expected_sha256(checksums.read_text(encoding="utf-8"), asset)
            actual = file_sha256(archive)
            if actual != expected:
                print(f"FAIL: Terraform {PINNED_TERRAFORM} checksum mismatch for {asset}", file=sys.stderr)
                print(f"  expected {expected}", file=sys.stderr)
                print(f"  actual   {actual}", file=sys.stderr)
                return 1
            with zipfile.ZipFile(archive) as zipped:
                zipped.extract("terraform", path=tmpdir)
            binary = dest / "terraform"
            shutil.copy2(tmpdir / "terraform", binary)
            binary.chmod(0o755)
    except (RuntimeError, OSError, zipfile.BadZipFile, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    version = terraform_version(str(binary))
    if version != PINNED_TERRAFORM:
        print(f"FAIL: installed terraform {version or 'unknown'} != {PINNED_TERRAFORM}", file=sys.stderr)
        return 1
    print(f"ok: installed pinned terraform {PINNED_TERRAFORM} at {binary}")
    return 0


def terraform_env() -> dict[str, str]:
    env = {
        "TF_IN_AUTOMATION": "1",
        "TF_INPUT": "0",
        "CHECKPOINT_DISABLE": "1",
    }
    for key in AWS_ENV:
        env[key] = ""
    return env


def run_terraform(binary: str, directory: Path) -> list[str]:
    errors: list[str] = []
    fmt = run_cmd([binary, "fmt", "-check", "-recursive", str(directory)], env=terraform_env())
    print_output(fmt)
    if fmt.returncode != 0:
        errors.append(f"terraform fmt -check failed for {directory.relative_to(ROOT)}")
    init = run_cmd(
        [binary, "init", "-backend=false", "-input=false", "-no-color"],
        cwd=directory,
        env=terraform_env(),
    )
    print_output(init)
    if init.returncode != 0:
        errors.append(f"terraform init -backend=false failed for {directory.relative_to(ROOT)}")
        return errors
    validate = run_cmd(
        [binary, "validate", "-no-color"],
        cwd=directory,
        env=terraform_env(),
    )
    print_output(validate)
    if validate.returncode != 0:
        errors.append(f"terraform validate failed for {directory.relative_to(ROOT)}")
    else:
        print(f"ok: terraform fmt/init -backend=false/validate passed for {directory.relative_to(ROOT)}")
    return errors


def run_checkov(binary: str, directory: Path) -> tuple[list[dict[str, Any]], list[str]]:
    output = ROOT / "checkov-report.json"
    result = run_cmd(
        [
            binary,
            "-d",
            str(directory),
            "--framework",
            "terraform",
            "--output",
            "json",
            "--soft-fail",
            "--compact",
            "--quiet",
        ],
        env=terraform_env(),
    )
    text = result.stdout.strip() or "{}"
    try:
        report = load_checkov_report(text)
    except (ValueError, json.JSONDecodeError) as exc:
        print_output(result)
        return [], [f"checkov JSON parse failed: {exc}"]
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if result.returncode not in {0, 1}:
        print_output(result)
        return [], ["checkov crashed"]
    findings = collect_checkov_findings(report)
    print(f"ok: checkov {PINNED_CHECKOV} retained {len(findings)} finding(s) for {directory.relative_to(ROOT)}")
    return findings, []


def check_ci_job() -> None:
    errors = ci_job_errors()
    if errors:
        print("FAIL: iac-scan CI job (#334)", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    print("ok: iac-scan CI job is required, pinned, and isolated from later slices")


def scan_repository(exceptions: list[dict[str, str]]) -> tuple[list[str], list[dict[str, Any]]]:
    terraform, checkov = require_live_tools()
    errors = run_terraform(terraform, STACK)
    checkov_findings, checkov_errors = run_checkov(checkov, STACK)
    errors.extend(checkov_errors)
    world_open = collect_world_open(terraform_files(STACK))
    findings = [*world_open, *checkov_findings]
    blocked = blocking_findings(findings, exceptions)
    unused = unused_exceptions(findings, exceptions, today_utc())
    if unused:
        errors.append("unused or expired IaC-scan exceptions")
        for item in unused:
            errors.append(f"{item['id']} {item['resource']} expires={item['expires']}")
    if blocked:
        errors.append("unaccepted world-open non-ALB or public-ingress IaC findings")
        for item in blocked:
            errors.append(f"{item['severity']} {item['id']} {item['resource']} {item.get('file', '')}")
    return errors, findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("all", "known-bad", "clean-baseline", "repo", "ci"),
        default="all",
    )
    parser.add_argument("--install-terraform", action="store_true")
    args = parser.parse_args(argv)
    if args.install_terraform:
        return install_terraform()
    try:
        exceptions = load_exceptions()
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    check_ci_job()
    if args.mode == "ci":
        return 0
    errors: list[str] = []
    if args.mode == "known-bad":
        errors.extend(prove_known_bad())
        if errors:
            print("FAIL: IaC scan gate (#334)", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        print("ok: known-bad world-open non-ALB fixture fails the IaC scan gate")
        return 0
    if args.mode == "clean-baseline":
        errors.extend(prove_clean_baseline())
        if errors:
            print("FAIL: IaC scan gate (#334)", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        print("ok: clean IaC baseline passed")
        return 0
    errors.extend(prove_known_bad())
    errors.extend(prove_clean_baseline())
    findings: list[dict[str, Any]] = []
    if args.mode in {"all", "repo"}:
        live_errors, findings = scan_repository(exceptions)
        errors.extend(live_errors)
        write_report(findings, errors)
    if errors:
        print("FAIL: IaC scan gate (#334)", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("ok: Terraform fmt/validate passed; world-open non-ALB ingress is absent or accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
