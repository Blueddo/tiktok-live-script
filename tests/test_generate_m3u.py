import os
import tempfile
import subprocess
from unittest import mock, TestCase

# Assumes generate_m3u.py is in repo root and exposes check_user_live, run_streamlink_and_get_url
import generate_m3u as gm

class FakeCompleted:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

class GenerateM3UTests(TestCase):
    def test_valid_stream_writes_m3u(self):
        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, "out.m3u")
            gm.OUTPUT_FILE = out_path
            # fake successful streamlink output with stream url
            fake = FakeCompleted(stdout="http://tiktokcdn.example/pull/stream.m3u8")
            with mock.patch("subprocess.run", return_value=fake):
                res = gm.check_user_live("user_one")
                # should report it is live
                self.assertIn("είναι σε live", res)
                # file should contain the url
                with open(out_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("http://tiktokcdn.example/pull/stream.m3u8", content)

    def test_timeout_reason(self):
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="streamlink", timeout=gm.TIMEOUT)):
            res = gm.check_user_live("user_two")
            self.assertIn("reason=timeout", res)

    def test_invalid_url_reason(self):
        fake = FakeCompleted(stdout="https://www.tiktok.com/@user_two")
        with mock.patch("subprocess.run", return_value=fake):
            res = gm.check_user_live("user_two")
            self.assertIn("reason=invalid_url", res)