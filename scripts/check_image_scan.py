#!/usr/bin/env python3
"""Scan deployable commit-SHA images and retain SBOMs (#332)."""

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
import tarfile
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".gitlab-ci.yml"
EXCEPTIONS = ROOT / "image-scan-exceptions.json"
REPORT = ROOT / "image-scan-report.json"
FIXTURES = ROOT / "scripts" / "fixtures" / "image-scan"
KNOWN_BAD_DOCKERFILE = FIXTURES / "known-bad.Dockerfile"
KNOWN_BAD_REPORT = FIXTURES / "known-bad-trivy.json"
CLEAN_REPORT = FIXTURES / "clean-trivy.json"
KNOWN_BAD_TAG = "aea/known-bad:seed"
KNOWN_BAD_IDS = frozenset({"CVE-2020-14343", "GHSA-6757-jp84-gxfx"})
PINNED_TRIVY = "0.74.0"
BLOCKING = frozenset({"HIGH", "CRITICAL"})
LATER_SLICES = ("checkov", "tfsec", "syft", "grype", "cosign")
OWNER_RE = re.compile(r"^@[a-z0-9][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DEPLOYABLE = (
    ("orchestration", "platform/Dockerfile.orchestration", "."),
    ("bff", "edge/bff/Dockerfile", "edge"),
    ("gateway", "edge/gateway/Dockerfile", "edge/gateway"),
    ("agent-runner", "platform/docker/Dockerfile.agent-runner", "."),
)
TRIVY_RELEASE = f"https://github.com/aquasecurity/trivy/releases/download/v{PINNED_TRIVY}"


def job_block(name: str) -> str:
    text = CI.read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(name)}:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not match:
        raise AssertionError(f"{name} job missing from .gitlab-ci.yml")
    return match.group(0)


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


def image_tag(name: str) -> str:
    sha = os.environ.get("CI_COMMIT_SHA") or "local"
    return f"aea/{name}:{sha}"


def load_exceptions(path: Path = EXCEPTIONS) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError("image-scan-exceptions.json missing")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("exceptions"), list):
        raise ValueError("image-scan-exceptions.json must be an object with an exceptions list")
    parsed: list[dict[str, str]] = []
    for index, item in enumerate(payload["exceptions"]):
        if not isinstance(item, dict):
            raise ValueError(f"exceptions[{index}] must be an object")
        required = ("id", "image", "package", "owner", "reason", "expires")
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
                "image": str(item["image"]).strip(),
                "package": str(item["package"]).strip(),
                "owner": owner,
                "reason": str(item["reason"]).strip(),
                "expires": expires,
            }
        )
    return parsed


def exception_active(item: dict[str, str], today: date) -> bool:
    return date.fromisoformat(item["expires"]) >= today


def load_trivy_report(payload: str | Path) -> dict[str, Any]:
    if isinstance(payload, Path):
        text = payload.read_text(encoding="utf-8")
    else:
        text = payload
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("trivy JSON must be an object")
    return data


def collect_findings(report: dict[str, Any], image: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    results = report.get("Results") or []
    if not isinstance(results, list):
        raise ValueError("trivy Results must be a list")
    for result in results:
        if not isinstance(result, dict):
            continue
        vulns = result.get("Vulnerabilities") or []
        if not isinstance(vulns, list):
            continue
        for vuln in vulns:
            if not isinstance(vuln, dict):
                continue
            vuln_id = str(vuln.get("VulnerabilityID") or "").strip()
            if not vuln_id:
                continue
            aliases = vuln.get("References") if isinstance(vuln.get("References"), list) else []
            extra_ids = {str(item).strip() for item in aliases if isinstance(item, str) and item.startswith(("CVE-", "GHSA-"))}
            findings.append(
                {
                    "image": image,
                    "id": vuln_id,
                    "aliases": sorted(extra_ids - {vuln_id}),
                    "package": str(vuln.get("PkgName") or "").strip(),
                    "installed": str(vuln.get("InstalledVersion") or "").strip(),
                    "fixed": str(vuln.get("FixedVersion") or "").strip(),
                    "severity": str(vuln.get("Severity") or "").strip().upper(),
                    "title": str(vuln.get("Title") or "").strip(),
                }
            )
    return findings


def classify_severity(finding: dict[str, Any]) -> str:
    severity = str(finding.get("severity") or "").upper()
    if severity in BLOCKING or severity in {"LOW", "MEDIUM"}:
        return severity
    return "HIGH"


def is_fixable(finding: dict[str, Any]) -> bool:
    return bool(str(finding.get("fixed") or "").strip())


def matching_exception(
    finding: dict[str, Any],
    exceptions: list[dict[str, str]],
    today: date,
) -> dict[str, str] | None:
    ids = {finding["id"], *finding.get("aliases", [])}
    for item in exceptions:
        if not exception_active(item, today):
            continue
        if item["id"] not in ids:
            continue
        if item["image"] not in {"*", finding["image"]}:
            continue
        if item["package"] not in {"*", finding["package"]}:
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
        finding["severity"] = classify_severity(finding)
        if finding["severity"] not in BLOCKING or not is_fixable(finding):
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
            ids = {finding["id"], *finding.get("aliases", [])}
            if item["id"] not in ids:
                continue
            if item["image"] not in {"*", finding["image"]}:
                continue
            if item["package"] not in {"*", finding["package"]}:
                continue
            matched = True
            break
        if not matched:
            unused.append(item)
    return unused


def prove_known_bad_report() -> list[str]:
    findings = collect_findings(load_trivy_report(KNOWN_BAD_REPORT), "known-bad")
    blocked = blocking_findings(findings, [])
    ids = set()
    for item in blocked:
        ids.update({item["id"], *item.get("aliases", [])})
    if not blocked or not (ids & KNOWN_BAD_IDS):
        return ["known-bad Trivy fixture unexpectedly passed High/Critical"]
    return []


def prove_clean_baseline() -> list[str]:
    findings = collect_findings(load_trivy_report(CLEAN_REPORT), "clean")
    blocked = blocking_findings(findings, [])
    if blocked:
        return ["clean Trivy fixture produced blocking findings"]
    return []


def ci_job_errors() -> list[str]:
    try:
        block = job_block("image-scan")
        digest_block = job_block("image-digest")
        deploy = job_block("deploy-ecs")
        deploy_agent = job_block("deploy-ecs-agent-runner")
        build = job_block("build-ecr")
        build_agent = job_block("build-ecr-agent-runner")
    except AssertionError as exc:
        return [str(exc)]
    errors: list[str] = []
    if "allow_failure:" in block:
        errors.append("image-scan must not set allow_failure")
    if "|| true" in block:
        errors.append("image-scan must not suppress failures")
    if PINNED_TRIVY not in block and f"v{PINNED_TRIVY}" not in block:
        if "--install-trivy" not in block:
            errors.append(f"image-scan must pin Trivy {PINNED_TRIVY}")
    if "scripts/check_image_scan.py" not in block:
        errors.append("image-scan must run scripts/check_image_scan.py")
    if "scripts/test_image_scan.py" not in block:
        errors.append("image-scan must run scripts/test_image_scan.py")
    if "--install-trivy" not in block:
        errors.append("image-scan must install the pinned Trivy release")
    if "image-scan-report.json" not in block:
        errors.append("image-scan must retain image-scan-report.json")
    if "sbom-" not in block:
        errors.append("image-scan must retain CycloneDX SBOMs")
    if "when: always" not in block:
        errors.append("image-scan must retain reports when: always")
    if "docker:27.1.1-dind" not in block:
        errors.append("image-scan must build commit-SHA images with pinned Docker-in-Docker")
    if any(token in block for token in LATER_SLICES):
        errors.append("image-scan must not stack #334 IaC scans")
    if "trivy" in digest_block or "sbom-" in digest_block:
        errors.append("image-digest must not stack #332 image SBOM/scan")
    if "job: image-scan" not in deploy:
        errors.append("deploy-ecs must depend on required image-scan")
    if "job: image-scan" not in deploy_agent:
        errors.append("deploy-ecs-agent-runner must depend on required image-scan")
    if re.search(r"^  needs:", build, re.M):
        errors.append("build-ecr must keep stage ordering so image-scan finishes before ECR push")
    if re.search(r"^  needs:", build_agent, re.M):
        errors.append("build-ecr-agent-runner must keep stage ordering so image-scan finishes before ECR push")
    return errors


def write_report(images: list[dict[str, Any]], findings: list[dict[str, Any]], errors: list[str]) -> None:
    payload = {
        "issue": 332,
        "ok": not errors,
        "trivy": PINNED_TRIVY,
        "images": images,
        "findings": findings,
        "blocking": [
            item
            for item in findings
            if item.get("severity") in BLOCKING and is_fixable(item) and not item.get("accepted")
        ],
        "errors": errors,
    }
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"ok: retained image scan report {REPORT.relative_to(ROOT)}")


def find_trivy() -> str:
    binary = shutil.which("trivy")
    if not binary:
        print(
            f"FAIL: trivy is not on PATH. Install the pinned release {PINNED_TRIVY} "
            "(python3 scripts/check_image_scan.py --install-trivy)",
            file=sys.stderr,
        )
        sys.exit(2)
    return binary


def trivy_version(binary: str) -> str:
    result = subprocess.run(
        [binary, "--version"],
        check=False,
        capture_output=True,
        text=True,
    )
    blob = f"{result.stdout}\n{result.stderr}"
    match = re.search(r"Version:\s*(\d+\.\d+\.\d+)", blob)
    return match.group(1) if match else ""


def require_live_scanner() -> tuple[str, str]:
    docker = shutil.which("docker")
    if not docker:
        print("FAIL: docker is required to build and scan commit-SHA images", file=sys.stderr)
        sys.exit(2)
    binary = find_trivy()
    version = trivy_version(binary)
    if version != PINNED_TRIVY:
        print(
            f"FAIL: trivy {version or 'unknown'} is not the pinned release {PINNED_TRIVY}",
            file=sys.stderr,
        )
        sys.exit(2)
    return binary, docker


def run_cmd(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd or ROOT, check=False, capture_output=True, text=True)


def print_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)


def trivy_asset() -> str:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        arch = "64bit"
    elif machine in {"aarch64", "arm64"}:
        arch = "ARM64"
    else:
        raise RuntimeError(f"unsupported machine for Trivy pin: {machine}")
    return f"trivy_{PINNED_TRIVY}_Linux-{arch}.tar.gz"


def download(url: str, dest: Path) -> None:
    curl = shutil.which("curl")
    if not curl:
        raise RuntimeError("curl is required to download the pinned Trivy release")
    result = run_cmd([curl, "-fsSL", "-o", str(dest), url])
    if result.returncode != 0 or not dest.is_file() or dest.stat().st_size == 0:
        print_output(result)
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
    raise ValueError(f"{filename} missing from Trivy checksums")


def install_trivy(dest_dir: Path | None = None) -> int:
    dest = dest_dir or Path(os.environ.get("TRIVY_INSTALL_DIR", "/usr/local/bin"))
    dest.mkdir(parents=True, exist_ok=True)
    asset = trivy_asset()
    with tempfile.TemporaryDirectory(prefix="trivy-pin-") as tmp:
        tmpdir = Path(tmp)
        archive = tmpdir / asset
        checksums = tmpdir / f"trivy_{PINNED_TRIVY}_checksums.txt"
        download(f"{TRIVY_RELEASE}/{asset}", archive)
        download(f"{TRIVY_RELEASE}/trivy_{PINNED_TRIVY}_checksums.txt", checksums)
        expected = expected_sha256(checksums.read_text(encoding="utf-8"), asset)
        actual = file_sha256(archive)
        if actual != expected:
            print(f"FAIL: Trivy {PINNED_TRIVY} checksum mismatch for {asset}", file=sys.stderr)
            print(f"  expected {expected}", file=sys.stderr)
            print(f"  actual   {actual}", file=sys.stderr)
            return 1
        with tarfile.open(archive, "r:gz") as tar:
            member = tar.getmember("trivy")
            try:
                tar.extract(member, path=tmpdir, filter="data")
            except TypeError:
                tar.extract(member, path=tmpdir)
        binary = dest / "trivy"
        shutil.copy2(tmpdir / "trivy", binary)
        binary.chmod(0o755)
    version = trivy_version(str(binary))
    if version != PINNED_TRIVY:
        print(f"FAIL: installed trivy {version or 'unknown'} != {PINNED_TRIVY}", file=sys.stderr)
        return 1
    print(f"ok: installed pinned trivy {PINNED_TRIVY} at {binary}")
    return 0


def docker_build(docker: str, dockerfile: Path, tag: str, context: Path) -> None:
    result = run_cmd(
        [
            docker,
            "build",
            "-f",
            str(dockerfile),
            "-t",
            tag,
            str(context),
        ]
    )
    print_output(result)
    if result.returncode != 0:
        raise RuntimeError(f"docker build failed for {tag}")


def trivy_image_json(binary: str, tag: str, output: Path) -> dict[str, Any]:
    result = run_cmd(
        [
            binary,
            "image",
            "--quiet",
            "--scanners",
            "vuln",
            "--severity",
            "HIGH,CRITICAL",
            "--ignore-unfixed",
            "--format",
            "json",
            "--output",
            str(output),
            tag,
        ]
    )
    print_output(result)
    if result.returncode not in {0, 1}:
        raise RuntimeError(f"trivy image scan crashed for {tag}")
    return load_trivy_report(output)


def trivy_sbom(binary: str, tag: str, output: Path) -> None:
    result = run_cmd(
        [
            binary,
            "image",
            "--quiet",
            "--format",
            "cyclonedx",
            "--output",
            str(output),
            tag,
        ]
    )
    print_output(result)
    if result.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"trivy SBOM failed for {tag}")


def prove_known_bad_live(binary: str, docker: str) -> list[str]:
    docker_build(docker, KNOWN_BAD_DOCKERFILE, KNOWN_BAD_TAG, FIXTURES)
    report_path = ROOT / "trivy-known-bad.json"
    report = trivy_image_json(binary, KNOWN_BAD_TAG, report_path)
    findings = collect_findings(report, "known-bad")
    blocked = blocking_findings(findings, [])
    ids = set()
    for item in blocked:
        ids.update({item["id"], *item.get("aliases", [])})
    if not blocked or not (ids & KNOWN_BAD_IDS):
        return ["seeded vulnerable image unexpectedly passed fixable High/Critical"]
    print(f"ok: seeded vulnerable image failed as expected ({', '.join(sorted(ids & KNOWN_BAD_IDS))})")
    return []


def scan_deployable(binary: str, docker: str, exceptions: list[dict[str, str]]) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    errors: list[str] = []
    images: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for name, dockerfile, context in DEPLOYABLE:
        dockerfile_path = ROOT / dockerfile
        context_path = ROOT / context
        if not dockerfile_path.is_file():
            errors.append(f"missing deployable Dockerfile: {dockerfile}")
            continue
        tag = image_tag(name)
        docker_build(docker, dockerfile_path, tag, context_path)
        report_path = ROOT / f"trivy-{name}.json"
        sbom_path = ROOT / f"sbom-{name}.json"
        report = trivy_image_json(binary, tag, report_path)
        trivy_sbom(binary, tag, sbom_path)
        image_findings = collect_findings(report, name)
        findings.extend(image_findings)
        images.append(
            {
                "name": name,
                "tag": tag,
                "dockerfile": dockerfile,
                "report": report_path.name,
                "sbom": sbom_path.name,
                "findings": len(image_findings),
            }
        )
        print(f"ok: scanned {tag} and retained {sbom_path.name}")
    blocked = blocking_findings(findings, exceptions)
    unused = unused_exceptions(findings, exceptions, today_utc())
    if unused:
        errors.append("unused or expired image-scan exceptions")
        for item in unused:
            errors.append(f"{item['id']} {item['image']} {item['package']} expires={item['expires']}")
    if blocked:
        errors.append("unaccepted fixable High/Critical image findings")
        for item in blocked:
            errors.append(
                f"{item['severity']} {item['id']} {item['image']} {item['package']}=={item['installed']} fix={item['fixed']}"
            )
    missing = [name for name, _df, _ctx in DEPLOYABLE if name not in {row["name"] for row in images}]
    if missing:
        errors.append("deployable images not scanned: " + ", ".join(missing))
    return errors, images, findings


def check_ci_job() -> None:
    errors = ci_job_errors()
    if errors:
        print("FAIL: image-scan CI job (#332)", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    print("ok: image-scan CI job is required, pinned, and isolated from #334")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("all", "known-bad", "clean-baseline", "repo", "ci"),
        default="all",
    )
    parser.add_argument("--install-trivy", action="store_true")
    args = parser.parse_args(argv)
    if args.install_trivy:
        return install_trivy()
    try:
        exceptions = load_exceptions()
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    check_ci_job()
    errors: list[str] = []
    if args.mode == "known-bad":
        errors.extend(prove_known_bad_report())
        if errors:
            print("FAIL: image scan gate (#332)", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        print("ok: known-bad Trivy fixture fails the image scan gate")
        return 0
    if args.mode == "clean-baseline":
        errors.extend(prove_clean_baseline())
        if errors:
            print("FAIL: image scan gate (#332)", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        print("ok: clean image-scan baseline passed")
        return 0
    if args.mode == "ci":
        return 0
    errors.extend(prove_known_bad_report())
    errors.extend(prove_clean_baseline())
    if errors:
        print("FAIL: image scan gate (#332)", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    images: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    if args.mode in {"all", "repo"}:
        binary, docker = require_live_scanner()
        if args.mode == "all":
            errors.extend(prove_known_bad_live(binary, docker))
        live_errors, images, findings = scan_deployable(binary, docker, exceptions)
        errors.extend(live_errors)
        write_report(images, findings, errors)
    if errors:
        print("FAIL: image scan gate (#332)", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("ok: deployable commit-SHA images scanned; fixable High/Critical are accepted or absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
