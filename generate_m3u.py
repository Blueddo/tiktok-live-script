#!/usr/bin/env python3
import concurrent.futures
import subprocess
import logging
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

def validate_config(cfg):
    """Basic validation and coercion for config values."""
    changed = False
    # timeout
    try:
        cfg["timeout"] = int(cfg.get("timeout", DEFAULTS["timeout"]))
    except Exception:
        cfg["timeout"] = DEFAULTS["timeout"]
    if cfg["timeout"] <= 0:
        cfg["timeout"] = DEFAULTS["timeout"]

    # max_workers
    try:
        cfg["max_workers"] = int(cfg.get("max_workers", DEFAULTS["max_workers"]))
    except Exception:
        cfg["max_workers"] = DEFAULTS["max_workers"]
    if cfg["max_workers"] <= 0:
        cfg["max_workers"] = DEFAULTS["max_workers"]

    # streamlink_args
    if not isinstance(cfg.get("streamlink_args", []), list):
        cfg["streamlink_args"] = DEFAULTS["streamlink_args"]

    # quality
    if not isinstance(cfg.get("quality", ""), str):
        cfg["quality"] = DEFAULTS["quality"]

    return cfg, changed

def load_config(path=CONFIG_PATH):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                cfg = {**DEFAULTS, **user_config}
                cfg, changed = validate_config(cfg)
                logger = logging.getLogger("tiktok")
                if changed:
                    logger.warning("Config coerced to valid types; using adjusted values.")
                logger.info(f"✅ Φορτώθηκε config.json από {path}")
                return cfg
        except Exception as e:
            logging.getLogger("tiktok").warning(f"⚠️ Σφάλμα στο config.json ({path}): {e}")
            return DEFAULTS
    else:
        logging.getLogger("tiktok").info(f"⚠️ Δεν βρέθηκε config.json στο {path}, χρησιμοποιούνται τα defaults.")
    return DEFAULTS

# -------- Logging setup --------
logger = logging.getLogger("tiktok")
logger.setLevel(logging.DEBUG)

# file handler (detailed debug logs)
fh = logging.FileHandler(os.path.join(BASE_DIR, "debug.log"), encoding="utf-8")
fh.setLevel(logging.DEBUG)
fh_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

# console handler (reduced)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)  # keep console cleaner for workflows
ch_formatter = logging.Formatter("%(levelname)s: %(message)s")
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

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

logger.debug("➡️ Script dir (BASE_DIR): %s", BASE_DIR)
logger.debug("➡️ Τρέχον working dir: %s", os.getcwd())
logger.info("➡️ Ενεργές ρυθμίσεις φορτωμένες")

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
        logger.info("Φορτώθηκαν %d χρήστες από το αρχείο %s.", len(users), USERS_FILE)
    except FileNotFoundError:
        logger.warning("Το αρχείο %s δεν βρέθηκε.", USERS_FILE)
    except Exception as e:
        logger.error("Σφάλμα κατά την ανάγνωση του αρχείου: %s", e)
    return users

# -------- Check user live --------
def run_streamlink_and_get_url(user, quality):
    """
    Επιστρέφει (url, returncode, stdout, stderr, reason)
    reason = None αν όλα καλά, αλλιώς 'timeout', 'file_not_found', 'streamlink_error', 'no_url'
    """
    cmd = ["streamlink", f"https://www.tiktok.com/@{user}", quality] + STREAMLINK_ARGS
    try:
        logger.debug("Running: %s (timeout=%s)", " ".join(cmd), TIMEOUT)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        logger.debug("returncode=%s; stdout_len=%d; stderr_len=%d", result.returncode, len(stdout), len(stderr))
        url = find_url_in_text(stdout) or find_url_in_text(stderr)
        reason = None
        if not url:
            reason = "no_url"
        return url, result.returncode, stdout, stderr, reason
    except subprocess.TimeoutExpired:
        logger.debug("Timeout για χρήστη %s (timeout=%ss)", user, TIMEOUT)
        return None, None, "", "TimeoutExpired", "timeout"
    except FileNotFoundError:
        logger.error("Το streamlink δεν βρέθηκε. Βεβαιώσου ότι είναι εγκατεστημένο και στο PATH.")
        return None, None, "", "FileNotFoundError", "file_not_found"
    except Exception as e:
        logger.exception("Σφάλμα κατά την εκτέλεση streamlink για %s: %s", user, e)
        return None, None, "", str(e), "streamlink_error"

def check_user_live(user):
    url, rc, out, err, reason = run_streamlink_and_get_url(user, QUALITY)

    if reason == "no_url" and QUALITY.lower() != "best":
        logger.debug("Δεν βρέθηκε URL με quality='%s' για %s. Δοκιμάζω fallback σε 'best'.", QUALITY, user)
        url, rc, out, err, reason = run_streamlink_and_get_url(user, "best")

    if url and is_valid_stream_url(url, user):
        status_msg = f"{user} είναι σε live -> {url}"
        logger.info(status_msg)
        with write_lock:
            try:
                with open(OUTPUT_FILE, "a", encoding="utf-8") as m3u_file:
                    m3u_file.write(
                        f"#EXTINF:-1 group-title=\"{GROUP_TITLE}\" tvg-logo=\"{TVG_LOGO}\" "
                        f"tvg-id=\"{TVG_ID}\" $ExtFilter=\"{EXT_FILTER}\",{{user}}\n"
                    )
                    m3u_file.write(f"{url}\n")
            except Exception as e:
                logger.error("Σφάλμα εγγραφής για %s: %s", user, e)
                return f"Σφάλμα εγγραφής για {user}: {e}"
        return f"Έλεγχος χρήστη: {status_msg}"

    if url and not is_valid_stream_url(url, user):
        reason = "invalid_url"

    debug_parts = []
    if rc is not None:
        debug_parts.append(f"rc={rc}")
    if err:
        debug_parts.append(f"stderr={err[:200]}")
    elif out:
        debug_parts.append(f"stdout={out[:200]}")
    debug = "; ".join(debug_parts) if debug_parts else "no debug output"

    logger.debug("User %s skipped -> reason=%s; %s", user, reason, debug)
    return f"Έλεγχος χρήστη: {user} - παραλήφθηκε -> reason={reason}; {debug}"

# -------- Main flow --------
def main():
    users = load_users()

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u_file:
            m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")
    except Exception as e:
        logger.error("Δεν μπορώ να γράψω το αρχείο %s: %s", OUTPUT_FILE, e)
        sys.exit(1)

    if not users:
        logger.info("Δεν υπάρχουν χρήστες για να ελεγχθούν. Έξοδος.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for result in executor.map(check_user_live, users):
            # print only summary to console (info), detailed traces are in debug.log
            logger.info(result)


if __name__ == "__main__":
    main()