"""
Unit tests for build_android_container.py helper.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import scripts.build_android_container as bac


class TestBuildAndroidContainer(unittest.TestCase):

    def test_get_local_java_major_version_parses_properly(self):
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = ""
            mock_proc.stderr = 'openjdk version "21.0.2" 2024-01-16\nOpenJDK Runtime'
            mock_run.return_value = mock_proc

            ver = bac.get_local_java_major_version()
            self.assertEqual(ver, 21)

    def test_get_local_java_major_version_parses_java_17(self):
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = 'java version "17.0.10" 2024-01-16'
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            ver = bac.get_local_java_major_version()
            self.assertEqual(ver, 17)

    def test_get_local_java_major_version_missing_java(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            ver = bac.get_local_java_major_version()
            self.assertEqual(ver, -1)

    @patch("scripts.build_android_container.get_local_java_major_version", return_value=17)
    @patch("scripts.build_android_container.run_docker_build", return_value=False)
    @patch("scripts.build_android_container.fetch_ci_debug_apk")
    def test_build_or_fetch_falls_back_to_ci_when_java17_and_no_docker(
        self, mock_fetch, mock_docker, mock_java
    ):
        mock_fetch.return_value = Path("/tmp/fake-app-debug.apk")
        res = bac.build_or_fetch(Path("/repo"), task="assembleDebug")
        self.assertEqual(res, Path("/tmp/fake-app-debug.apk"))
        mock_fetch.assert_called_once()

    @patch("scripts.build_android_container.get_local_java_major_version", return_value=21)
    @patch("subprocess.run")
    def test_build_or_fetch_uses_local_when_java21(self, mock_run, mock_java):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        with patch.object(Path, "exists", return_value=True):
            res = bac.build_or_fetch(Path("/repo"), task="assembleDebug")
            self.assertIsNotNone(res)
            mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
