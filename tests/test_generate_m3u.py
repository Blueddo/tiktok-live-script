import os
import sys
import time
import logging
from unittest import TestCase

# Προσθήκη root στο sys.path για να βρει το generate_m3u.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import generate_m3u as gm

# Logger για τα tests
logging.basicConfig(level=logging.INFO, format="[TEST] %(message)s")
logger = logging.getLogger("GenerateM3UTests")

class GenerateM3URealTests(TestCase):

    @classmethod
    def setUpClass(cls):
        # Διαβάζουμε τους πραγματικούς test users
        users_file = os.path.join(os.path.dirname(__file__), "users_test.txt")
        with open(users_file, "r", encoding="utf-8") as f:
            cls.test_users = [line.strip() for line in f if line.strip()]

    def test_generate_m3u_real_users(self):
        """Δημιουργεί πραγματικό M3U και καταγράφει αναλυτικά αποτελέσματα για κάθε χρήστη"""
        out_m3u = os.path.join(os.path.dirname(__file__), "test_output.m3u")
        log_file = os.path.join(os.path.dirname(__file__), "test_output.log")
        gm.OUTPUT_FILE = out_m3u

        with open(log_file, "w", encoding="utf-8") as logf:
            start_total = time.perf_counter()
            for user in self.test_users:
                start = time.perf_counter()
                result = gm.check_user_live(user)
                duration = time.perf_counter() - start

                # Εξαγωγή πληροφοριών: live ή όχι, reason, rc, stderr
                # Υποθέτουμε ότι το generate_m3u.py επιστρέφει μια string με λόγο ή live URL
                log_line = f"User: {user} | Result: {result} | Checked in: {duration:.2f} sec"
                logger.info(log_line)
                logf.write(log_line + "\n")

            total_duration = time.perf_counter() - start_total
            summary = f"Processed {len(self.test_users)} users in {total_duration:.2f} sec | M3U: {out_m3u}"
            logger.info(summary)
            logf.write(summary + "\n")

        # Επιβεβαίωση ότι δημιουργήθηκε το M3U
        self.assertTrue(os.path.exists(out_m3u), "Το M3U αρχείο δεν δημιουργήθηκε")
        # Προαιρετικός έλεγχος ότι έχει γραμμένη τουλάχιστον μια γραμμή
        with open(out_m3u, "r", encoding="utf-8") as f:
            content = f.read().strip()
        self.assertTrue(len(content) > 0, "Το M3U αρχείο είναι άδειο")
