"""
Containerized Android Build & CI Artifact Downloader Wrapper.

Provides seamless local building and artifact retrieval regardless of host JDK:
1. Direct Gradle build if local JDK >= 21.
2. Containerized build via Docker (`cimg/android:2024.04`) if local JDK is incompatible.
3. Fast-path CI artifact downloader via `glab api` if Docker/JDK are unavailable.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def get_local_java_major_version() -> int:
    """Returns local Java major version or -1 if java is missing/unparseable."""
    try:
        proc = subprocess.run(["java", "-version"], capture_output=True, text=True)
        combined = proc.stdout + "\n" + proc.stderr
        # Parse version like "21.0.2", "17.0.20", "1.8.0_xxx"
        match = re.search(r'version\s+"(\d+)(?:\.(\d+))?', combined)
        if match:
            major = int(match.group(1))
            if major == 1 and match.group(2):
                return int(match.group(2))
            return major
    except Exception:
        pass
    return -1


def fetch_ci_debug_apk(dest_dir: Path, pipeline_id: str | None = None) -> Path | None:
    """Downloads and extracts app-debug.apk from GitLab CI via glab."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    project_encoded = "artof-group%2Fadaptive-experience-architecture"

    job_id = None
    if pipeline_id:
        url = f"projects/{project_encoded}/pipelines/{pipeline_id}/jobs"
        try:
            out = subprocess.check_output(["glab", "api", url], text=True)
            jobs = json.loads(out)
            for j in jobs:
                if j.get("name") == "android-build-debug" and j.get("status") == "success":
                    job_id = j.get("id")
                    break
        except Exception as e:
            print(f"Error fetching jobs for pipeline {pipeline_id}: {e}", file=sys.stderr)

    if not job_id:
        # Get latest successful pipeline on main
        url = f"projects/{project_encoded}/pipelines?ref=main&status=success&per_page=5"
        try:
            out = subprocess.check_output(["glab", "api", url], text=True)
            pipelines = json.loads(out)
            for p in pipelines:
                p_id = p.get("id")
                jobs_out = subprocess.check_output(
                    ["glab", "api", f"projects/{project_encoded}/pipelines/{p_id}/jobs"],
                    text=True,
                )
                for j in json.loads(jobs_out):
                    if j.get("name") == "android-build-debug" and j.get("status") == "success":
                        job_id = j.get("id")
                        break
                if job_id:
                    break
        except Exception as e:
            print(f"Error querying pipelines: {e}", file=sys.stderr)

    if not job_id:
        print("No successful android-build-debug job found in recent pipelines.", file=sys.stderr)
        return None

    zip_path = dest_dir / "ci_artifacts.zip"
    try:
        cmd = ["glab", "api", f"projects/{project_encoded}/jobs/{job_id}/artifacts"]
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode != 0 or len(res.stdout) == 0:
            print(f"Failed to download job {job_id} artifacts: {res.stderr}", file=sys.stderr)
            return None

        zip_path.write_bytes(res.stdout)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(dest_dir)
        zip_path.unlink(missing_ok=True)

        for apk in dest_dir.rglob("*.apk"):
            if "debug" in apk.name.lower():
                return apk
    except Exception as e:
        print(f"Extraction failed: {e}", file=sys.stderr)
    return None


def run_docker_build(
    repo_root: Path,
    task: str = "assembleDebug",
    image: str = "cimg/android:2024.04",
) -> bool:
    """Executes Gradle build inside Docker container."""
    android_dir = repo_root / "clients" / "mobile" / "android"
    # Ensure gradlew has execute permission
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{android_dir.resolve()}:/home/circleci/project",
        "-w",
        "/home/circleci/project",
        image,
        "sh",
        "-c",
        f"chmod +x ./gradlew && ./gradlew {task}",
    ]
    try:
        proc = subprocess.run(cmd)
        return proc.returncode == 0
    except Exception as e:
        print(f"Docker build execution failed: {e}", file=sys.stderr)
        return False


def build_or_fetch(
    repo_root: Path,
    task: str = "assembleDebug",
    force_ci: bool = False,
    force_docker: bool = False,
) -> Path | None:
    """Orchestrates local build vs docker build vs CI artifact fetch."""
    android_dir = repo_root / "clients" / "mobile" / "android"
    output_apk = (
        android_dir / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
    )

    if force_ci:
        print("[CI-FETCH] Downloading latest debug APK from GitLab CI...")
        fetch_dir = repo_root / "build_artifacts"
        return fetch_ci_debug_apk(fetch_dir)

    java_ver = get_local_java_major_version()
    if java_ver >= 21 and not force_docker:
        print(f"[LOCAL] Local Java version {java_ver} >= 21 detected. Running local Gradle...")
        gradlew = android_dir / ("gradlew.bat" if sys.platform == "win32" else "gradlew")
        res = subprocess.run([str(gradlew), task], cwd=android_dir)
        if res.returncode == 0 and output_apk.exists():
            return output_apk

    print(f"[DOCKER] Local Java ({java_ver}) < 21. Attempting containerized Docker build...")
    if run_docker_build(repo_root, task=task):
        if output_apk.exists():
            return output_apk

    print("[FALLBACK] Docker unavailable or failed. Falling back to CI artifact download...")
    fetch_dir = repo_root / "build_artifacts"
    return fetch_ci_debug_apk(fetch_dir)


def main():
    parser = argparse.ArgumentParser(description="Containerized Android build & CI downloader")
    parser.add_argument("--task", default="assembleDebug", help="Gradle task to run")
    parser.add_argument("--fetch-ci", action="store_true", help="Directly download from CI")
    parser.add_argument("--pipeline-id", help="Optional specific pipeline ID to pull from")
    parser.add_argument("--docker", action="store_true", help="Force Docker build")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    if args.fetch_ci:
        apk = fetch_ci_debug_apk(repo_root / "build_artifacts", pipeline_id=args.pipeline_id)
    else:
        apk = build_or_fetch(repo_root, task=args.task, force_docker=args.docker)

    if apk and apk.exists():
        print(f"[SUCCESS] Target APK ready at: {apk}")
        sys.exit(0)
    else:
        print("[ERROR] Failed to build or retrieve Android APK.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
