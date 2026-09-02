#!/usr/bin/env python3
"""Upload a signed AAB to Google Play internal/closed testing (#354).

Uses the Google Play Android Developer API (edits → bundles.upload →
tracks.update → edits.commit). Defaults to track ``internal`` (Play internal
testing). Override with ``--track`` / ``PLAY_TRACK`` for a closed-testing API
track name (often ``alpha`` or a custom Console track). Never uploads to
``production``.

Credentials: GitLab protected **File** variable ``PLAY_API_SERVICE_ACCOUNT_JSON``
(service-account JSON). Agents do not create or paste that secret.

Honesty:
  - Dry-run / skip when credentials or AAB are absent — not a successful upload.
  - Upload success ≠ Production. Do not open the production track.
  - Play rejects a duplicate ``versionCode``; bump ``versionCode`` in
    ``clients/mobile/android/app/build.gradle.kts`` before re-upload.
  - App Distribution / debug APK ≠ Play install path.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

DEFAULT_PACKAGE = "link.artof.aea.companion"
DEFAULT_TRACK = "internal"
DEFAULT_AAB = (
    "clients/mobile/android/app/build/outputs/bundle/release/app-release.aab"
)
ANDROIDPUBLISHER_SCOPE = "https://www.googleapis.com/auth/androidpublisher"
FORBIDDEN_TRACKS = frozenset({"production", "prod"})


def resolve_credentials_path(explicit: str | None) -> Path | None:
    """Return a readable service-account JSON path, or None if unset/missing."""
    raw = (explicit or os.environ.get("PLAY_API_SERVICE_ACCOUNT_JSON") or "").strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.is_file():
        return None
    return path


def resolve_aab_path(explicit: str | None) -> Path | None:
    raw = (explicit or os.environ.get("PLAY_AAB_PATH") or DEFAULT_AAB).strip()
    path = Path(raw)
    if not path.is_file():
        return None
    return path


def normalize_track(track: str) -> str:
    return track.strip().lower()


def assert_track_allowed(track: str) -> str:
    name = normalize_track(track)
    if not name:
        raise ValueError("track name is empty")
    if name in FORBIDDEN_TRACKS:
        raise ValueError(
            f"refusing track {track!r}: Production is out of scope for #354 "
            "(internal/closed testing only)"
        )
    return name


def build_release_body(version_code: int, status: str = "completed") -> dict[str, Any]:
    """Track update body for a single-version release."""
    return {
        "releases": [
            {
                "versionCodes": [str(version_code)],
                "status": status,
            }
        ]
    }


def dry_run_report(
    *,
    package_name: str,
    track: str,
    aab: Path | None,
    credentials: Path | None,
) -> dict[str, Any]:
    return {
        "mode": "dry-run",
        "package_name": package_name,
        "track": track,
        "aab": str(aab) if aab else None,
        "aab_present": aab is not None,
        "credentials_present": credentials is not None,
        "would_call": [
            "edits.insert",
            "edits.bundles.upload",
            "edits.tracks.update",
            "edits.commit",
        ],
        "forbidden_tracks": sorted(FORBIDDEN_TRACKS),
        "notes": [
            "Dry-run does not contact Google Play.",
            "versionCode must be incremented vs the last uploaded bundle or Play rejects the edit.",
            "Never artifact PLAY_API_SERVICE_ACCOUNT_JSON.",
        ],
    }


def upload_aab(
    *,
    package_name: str,
    track: str,
    aab: Path,
    credentials: Path,
    release_status: str = "completed",
) -> dict[str, Any]:
    """Perform the Play edits upload. Requires google-api-python-client + google-auth."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:  # pragma: no cover - exercised in CI when deps missing
        raise SystemExit(
            "FAIL: google-api-python-client / google-auth not installed. "
            "CI should pip-install them before calling this script. "
            f"({exc})"
        ) from exc

    track_name = assert_track_allowed(track)
    creds = service_account.Credentials.from_service_account_file(
        str(credentials),
        scopes=[ANDROIDPUBLISHER_SCOPE],
    )
    service = build("androidpublisher", "v3", credentials=creds, cache_discovery=False)

    edit = service.edits().insert(body={}, packageName=package_name).execute()
    edit_id = edit["id"]
    print(f"ok: created edit {edit_id}", flush=True)

    media = MediaFileUpload(str(aab), mimetype="application/octet-stream", resumable=True)
    bundle = (
        service.edits()
        .bundles()
        .upload(
            packageName=package_name,
            editId=edit_id,
            media_body=media,
        )
        .execute()
    )
    version_code = int(bundle["versionCode"])
    print(
        f"ok: uploaded bundle versionCode={version_code} "
        f"sha1={bundle.get('sha1', '?')}",
        flush=True,
    )

    track_body = build_release_body(version_code, status=release_status)
    track_resp = (
        service.edits()
        .tracks()
        .update(
            packageName=package_name,
            editId=edit_id,
            track=track_name,
            body=track_body,
        )
        .execute()
    )
    print(f"ok: track {track_name} updated → {json.dumps(track_resp, default=str)[:400]}", flush=True)

    commit = service.edits().commit(packageName=package_name, editId=edit_id).execute()
    print(f"ok: committed edit {commit.get('id', edit_id)}", flush=True)

    return {
        "mode": "upload",
        "package_name": package_name,
        "track": track_name,
        "edit_id": edit_id,
        "version_code": version_code,
        "sha1": bundle.get("sha1"),
        "sha256": bundle.get("sha256"),
        "release_status": release_status,
        "committed": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package-name",
        default=os.environ.get("PLAY_PACKAGE_NAME", DEFAULT_PACKAGE),
        help=f"Android applicationId (default {DEFAULT_PACKAGE})",
    )
    parser.add_argument(
        "--track",
        default=os.environ.get("PLAY_TRACK", DEFAULT_TRACK),
        help="Play API track name (default internal). Not production.",
    )
    parser.add_argument(
        "--aab",
        default=None,
        help=f"Path to signed .aab (default {DEFAULT_AAB} or PLAY_AAB_PATH)",
    )
    parser.add_argument(
        "--credentials",
        default=None,
        help="Path to service-account JSON (or PLAY_API_SERVICE_ACCOUNT_JSON)",
    )
    parser.add_argument(
        "--release-status",
        default=os.environ.get("PLAY_RELEASE_STATUS", "completed"),
        choices=("completed", "draft", "halted", "inProgress"),
        help="Track release status (default completed)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print plan; do not call Google APIs",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        help="Optional path to write a JSON summary",
    )
    args = parser.parse_args(argv)

    try:
        track = assert_track_allowed(args.track)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    credentials = resolve_credentials_path(args.credentials)
    aab = resolve_aab_path(args.aab)

    if args.dry_run:
        report = dry_run_report(
            package_name=args.package_name,
            track=track,
            aab=aab,
            credentials=credentials,
        )
        print(json.dumps(report, indent=2))
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(
            "DRY-RUN: no Play API calls. Provide PLAY_API_SERVICE_ACCOUNT_JSON + "
            "a signed .aab and omit --dry-run for a real upload.",
            flush=True,
        )
        return 0

    if credentials is None:
        print(
            "SKIP: PLAY_API_SERVICE_ACCOUNT_JSON file variable is not available.",
            flush=True,
        )
        print(
            "Protected file secrets are typically unset on unprotected branches.",
            flush=True,
        )
        print(
            "Sponsor must add PLAY_API_SERVICE_ACCOUNT_JSON (Play API service-account "
            "JSON, Type File, Protected) in GitLab CI/CD → Variables.",
            flush=True,
        )
        print(
            "Grant the SA on the Play Console app (release to internal/closed track only). "
            "Do not paste JSON in issues/MRs/chat. This is not a Play upload.",
            flush=True,
        )
        return 1

    if aab is None:
        print(
            "SKIP: signed app-release.aab not found "
            f"(looked for {args.aab or os.environ.get('PLAY_AAB_PATH') or DEFAULT_AAB}).",
            flush=True,
        )
        print(
            "Run android-bundle-release first (or rebuild with ANDROID_UPLOAD_* vars).",
            flush=True,
        )
        print("This is not a Play upload.", flush=True)
        return 1

    # Copy credentials to a job-local path pattern is handled by CI; here we
    # only refuse to print contents.
    print(
        f"ok: using credentials file at job-local path (not printing; not an artifact)",
        flush=True,
    )
    print(f"ok: aab={aab} size={aab.stat().st_size} bytes", flush=True)

    report = upload_aab(
        package_name=args.package_name,
        track=track,
        aab=aab,
        credentials=credentials,
        release_status=args.release_status,
    )
    print(json.dumps(report, indent=2))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
