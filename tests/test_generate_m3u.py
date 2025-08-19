import os
import sys
import time
import logging
import subprocess
import tempfile
from unittest import mock, TestCase

# Προσθήκη root στο sys.path για να βρει το generate_m3u.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import generate_m3u as gm

# Logger για τα tests
logging.basicConfig(level=logging.INFO, format="[TEST] %(message)s")
logger = logging.getLogger("GenerateM3UTests")

class FakeCompleted:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

class GenerateM3UTests(TestCase):

    @classmethod
    def setUpClass(cls):
        # Φόρτωση των test χρηστών από το tests/users_test.txt
        users_file = os.path.join(os.path.dirname(__file__), "users_test.txt")
        with open(users_file, "r", encoding="utf-8") as f:
            cls.test_users = [line.strip() for line in f if line.strip()]

    def test_generate_m3u_from_users_test(self):
        """Δημιουργεί δοκιμαστικό M3U για όλους τους χρήστες στο users_test.txt"""
        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, "test_output.m3u")
            gm.OUTPUT_FILE = out_path
            fake = FakeCompleted(stdout="http://tiktokcdn.example/pull/stream.m3u8")

            with mock.patch("subprocess.run", return_value=fake):
                start = time.perf_counter()
                for user in self.test_users:
                    res = gm.check_user_live(user)
                    self.assertIn("είναι σε live", res)
                duration = time.perf_counter() - start
                logger.info(f"Generated test M3U for {len(self.test_users)} users in {duration:.4f} sec")

            # Αντιγραφή του αρχείου M3U στο φάκελο tests
            final_m3u = os.path.join(os.path.dirname(__file__), "test_output.m3u")
            if os.path.exists(out_path):
                with open(out_path, "r", encoding="utf-8") as src:
                    content = src.read()
                with open(final_m3u, "w", encoding="utf-8") as dst:
                    dst.write(content)
                logger.info(f"Test M3U written to {final_m3u}")
            else:
                logger.warning("No M3U file produced during test")

    def test_timeout_reason(self):
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="streamlink", timeout=gm.TIMEOUT)):
            start = time.perf_counter()
            res = gm.check_user_live("user_timeout")
            duration = time.perf_counter() - start
            logger.info(f"Timeout test took {duration:.4f} sec")
            self.assertIn("reason=timeout", res)

    def test_invalid_url_reason(self):
        fake = FakeCompleted(stdout="https://www.tiktok.com/@user_invalid")
        with mock.patch("subprocess.run", return_value=fake):
            res = gm.check_user_live("user_invalid")
            self.assertIn("reason=invalid_url", res)

    def test_empty_stdout_reason(self):
        fake = FakeCompleted(stdout="")
        with mock.patch("subprocess.run", return_value=fake):
            res = gm.check_user_live("user_empty")
            self.assertIn("reason=invalid_url", res)

    def test_non_zero_return_code(self):
        fake = FakeCompleted(stdout="", stderr="error", returncode=1)
        with mock.patch("subprocess.run", return_value=fake):
            res = gm.check_user_live("user_fail")
            self.assertIn("reason=non_zero_return", res)

    def test_batch_performance(self):
        """Μετράει χρόνο εκτέλεσης για όλους τους test users"""
        fake = FakeCompleted(stdout="http://tiktokcdn.example/pull/stream.m3u8")
        with mock.patch("subprocess.run", return_value=fake):
            start = time.perf_counter()
            results = [gm.check_user_live(u) for u in self.test_users]
            duration = time.perf_counter() - start
            avg = duration / len(self.test_users)
            logger.info(f"Processed {len(self.test_users)} users in {duration:.4f} sec, avg {avg:.4f} sec/user")
            for res in results:
                self.assertIn("είναι σε live", res)
