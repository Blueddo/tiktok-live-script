#!/usr/bin/env python3
import concurrent.futures
import subprocess
from tqdm import tqdm
from termcolor import colored
import json
import os
import sys
import re
import threading

# -------- CONFIG LOADER --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

DEFAULTS = {
    "quality": "worst",
    "timeout": 10,
    "max_workers": 10,
    "output_file": "tiktok_live.m3u",
    "users_file": "userstiktok.txt",
    "group_title": "TikTok Live",
    "tvg_logo": "https://www.tiktok.com/favicon.ico",
    "tvg_id": "simpleTVFakeEpgId",
    "ext_filter": "TikTok live",
    "streamlink_args": ["--stream-url"]
}

def load_config(path=CONFIG_PATH):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                cfg = {**DEFAULTS, **user_config}
                print(f"✅ Φορτώθηκε config.json από {path}")
                return cfg
        except Exception as e:
            print(f"⚠️ Σφάλμα στο config.json ({path}): {e}")
            return DEFAULTS
    else:
        print(f"⚠️ Δεν βρέθηκε config.json στο {path}, χρησιμοποιούνται τα defaults.")
    return DEFAULTS

config = load_config()

QUALITY = config.get("quality", DEFAULTS["quality"])
TIMEOUT = config.get("timeout", DEFAULTS["timeout"])
MAX_WORKERS = config.get("max_workers", DEFAULTS["max_workers"])
OUTPUT_FILE = os.path.join(BASE_DIR, config.get("output_file", DEFAULTS["output_file"]))
USERS_FILE = os.path.join(BASE_DIR, config.get("users_file", DEFAULTS["users_file"]))
GROUP_TITLE = config.get("group_title", DEFAULTS["group_title"])
TVG_LOGO = config.get("tvg_logo", DEFAULTS["tvg_logo"])
TVG_ID = config.get("tvg_id", DEFAULTS["tvg_id"])
EXT_FILTER = config.get("ext_filter", DEFAULTS["ext_filter"])
STREAMLINK_ARGS = config.get("streamlink_args", DEFAULTS["streamlink_args"]) or DEFAULTS["streamlink_args"]

print("➡️ Script dir (BASE_DIR):", BASE_DIR)
print("➡️ Τρέχον working dir:", os.getcwd())
print("➡️ Ενεργές ρυθμίσεις:", config)

# -------- Helpers --------
url_re = re.compile(r"https?://\S+")
write_lock = threading.Lock()

def find_url_in_text(text):
    if not text:
        return None
    m = url_re.search(text)
    return m.group(0) if m else None

def is_valid_stream_url(url, user):
    """
    Απλός έλεγχος: απορρίπτει link προφίλ και αποδέχεται κοινά stream markers.
    """
    if not url:
        return False
    u = url.strip().lower()
    if u.startswith(f"https://www.tiktok.com/@{user.lower()}"):
        return False
    stream_markers = ("tiktokcdn", "pull-", "/stage/", "/game/", "stream-", ".flv", ".m3u8", ".ts", ".mp4")
    return any(marker in u for marker in stream_markers)

# -------- Load users --------
def load_users():
    users = []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                users.append(line)
        print(f"Φορτώθηκαν {len(users)} ��ρήστες από το αρχείο {USERS_FILE}.")
    except FileNotFoundError:
        print(f"Το αρχείο {USERS_FILE} δεν βρέθηκε.")
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
    return users

# -------- Check user live --------
def run_streamlink_and_get_url(user, quality):
    """
    Επιστρέφει (url, returncode, stdout, stderr, reason)
    reason = None αν όλα καλά, αλλιώς 'timeout', 'file_not_found', 'streamlink_error', 'no_url'
    """
    cmd = ["streamlink", f"https://www.tiktok.com/@{user}", quality] + STREAMLINK_ARGS
    try:
        print(f"👉 Running: {' '.join(cmd)} (timeout={TIMEOUT})")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        print(f"   returncode={result.returncode}; stdout_len={len(stdout)}; stderr_len={len(stderr)}")
        url = find_url_in_text(stdout) or find_url_in_text(stderr)
        reason = None
        if not url:
            reason = "no_url"
        return url, result.returncode, stdout, stderr, reason
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout για χρήστη {user} (timeout={TIMEOUT}s)")
        return None, None, "", "TimeoutExpired", "timeout"
    except FileNotFoundError:
        print("❌ Το streamlink δεν βρέθηκε. Βεβαιώσου ότι είναι εγκατεστημένο (pip install streamlink) και στο PATH.")
        return None, None, "", "FileNotFoundError", "file_not_found"
    except Exception as e:
        print(f"⚠️ Σφάλμα κατά την εκτέλεση streamlink για {user}: {e}")
        return None, None, "", str(e), "streamlink_error"

def check_user_live(user):
    # Προσπαθούμε με την επιλεγμένη ποιότητα πρώτα
    url, rc, out, err, reason = run_streamlink_and_get_url(user, QUALITY)

    # Fallback σε best αν χρειαστεί
    if reason == "no_url" and QUALITY.lower() != "best":
        print(f"   Δεν βρέθηκε URL με quality='{QUALITY}' για {user}. Δοκιμάζω fallback σε 'best'.")
        url, rc, out, err, reason = run_streamlink_and_get_url(user, "best")

    # Αν βρέθηκε url και φαίνεται έγκυρο, γράφουμε στο m3u
    if url and is_valid_stream_url(url, user):
        status = colored("είναι σε live", "yellow", "on_blue", attrs=["bold"])
        with write_lock:
            try:
                with open(OUTPUT_FILE, "a", encoding="utf-8") as m3u_file:
                    m3u_file.write(
                        f"#EXTINF:-1 group-title=\"{GROUP_TITLE}\" tvg-logo=\"{TVG_LOGO}\" "
                        f"tvg-id=\"{TVG_ID}\" $ExtFilter=\"{EXT_FILTER}\",{{user}}\n"
                    )
                    m3u_file.write(f"{{url}}\n")
            except Exception as e:
                return f"Σφάλμα εγγραφής για {user}: {e}"
        return f"Έλεγχος χρήστη: {user} - {status} -> {url}"

    # Αλλιώς δεν γράφουμε στο m3u — δημιουργούμε λεπτομερές log για το γιατί παραλήφθηκε
    # reason μπορεί να είναι: timeout, file_not_found, streamlink_error, no_url, invalid_url
    if url and not is_valid_stream_url(url, user):
        reason = "invalid_url"

    # Συνθέτουμε ένα χρήσιμο μήνυμα με αιτία και λίγα debug bits (rc, stderr/stdout truncated)
    debug_parts = []
    if rc is not None:
        debug_parts.append(f"rc={rc}")
    if err:
        debug_parts.append(f"stderr={err[:200]}")
    elif out:
        debug_parts.append(f"stdout={out[:200]}")
    debug = "; ".join(debug_parts) if debug_parts else "no debug output"

    return f"Έλεγχος χρήστη: {user} - παραλήφθηκε -> reason={reason}; {debug}"

# -------- Main flow --------
def main():
    users = load_users()

    # Δημιουργία/επανεγγραφή αρχείου m3u με header
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u_file:
            m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")
    except Exception as e:
        print(f"⚠️ Δεν μπορώ να γράψω το αρχείο {OUTPUT_FILE}: {e}")
        sys.exit(1)

    if not users:
        print("Δεν υπάρχουν χρήστες για να ελεγχθούν. Έξοδος.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(
            tqdm(
                executor.map(check_user_live, users),
                total=len(users),
                desc="Έλεγχος χ��ηστών του tiktok",
                ncols=120,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}"
            )
        )
        for result in results:
            tqdm.write(result)

if __name__ == "__main__":
    main()