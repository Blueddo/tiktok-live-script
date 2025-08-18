import concurrent.futures
import subprocess
from tqdm import tqdm
from termcolor import colored
import json
import os
import sys

# -------- BLOCK: CONFIG LOADER --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

# Συνάρτηση φόρτωσης προεπιλεγμένων ρυθμίσεων από αρχείο
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

# Συνάρτηση φόρτωσης ρυθμισεων από αρχείο
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

QUALITY = config["quality"]
TIMEOUT = config["timeout"]
MAX_WORKERS = config["max_workers"]
OUTPUT_FILE = config["output_file"]
USERS_FILE = config["users_file"]
GROUP_TITLE = config["group_title"]
TVG_LOGO = config["tvg_logo"]
TVG_ID = config["tvg_id"]
EXT_FILTER = config["ext_filter"]
STREAMLINK_ARGS = config["streamlink_args"]

print("➡️ Τρέχον working dir:", os.getcwd())
print("➡️ Αρχεία στον φάκελο:", os.listdir(BASE_DIR))
print("➡️ Ενεργές ρυθμίσεις:", config)
# -------- ΤΕΛΟΣ BLOCK --------


# Συνάρτηση φόρτωσης χρηστών από αρχείο
def load_users():
    users = []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                users.append(line)
        print(f"Φορτώθηκαν {len(users)} χρήστες από το αρχείο {USERS_FILE}.")
    except FileNotFoundError:
        print(f"Το αρχείο {USERS_FILE} δεν βρέθηκε.")
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
    return users


# Συνάρτηση ελέγχου αν ο χρήστης είναι live
def check_user_live(user):
    try:
        cmd = ["streamlink", f"https://www.tiktok.com/@{user}", QUALITY] + STREAMLINK_ARGS
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=TIMEOUT
        )
        output = result.stdout.strip()
        
        if output.startswith("http"):
            status = colored("είναι σε live", "yellow", "on_blue", attrs=["bold", "blink"])
            with open(OUTPUT_FILE, "a", encoding="utf-8") as m3u_file:
                m3u_file.write(
                    f"#EXTINF:-1 group-title=\"{GROUP_TITLE}\" tvg-logo=\"{TVG_LOGO}\" "
                    f"tvg-id=\"{TVG_ID}\" $ExtFilter=\"{EXT_FILTER}\",{user}\n"
                )
                m3u_file.write(f"{output}\n")
            return f"Έλεγχος χρήστη: {user} - {status}"
        else:
            return f"Έλεγχος χρήστη: {user} - δεν είναι σε live"
    except Exception as e:
        return f"Σφάλμα κατά τον έλεγχο του χρήστη {user}: {e}"


# Φόρτωση χρηστών από το αρχείο
users = load_users()

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u_file:
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

# Έλεγχος για κάθε χρήστη αν είναι live με παράλληλη εκτέλεση
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    results = list(
        tqdm(
            executor.map(check_user_live, users),
            total=len(users),
            desc="Έλεγχος χρηστών του tiktok",
            ncols=120,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}'
        )
    )
    for result in results:
        tqdm.write(result)


import concurrent.futures
import subprocess
from tqdm import tqdm
from termcolor import colored
import json
import os

# Συνάρτηση φόρτωσης ρυθμισεων από αρχείο
def load_config(path="config.json"):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Σφάλμα στο config.json: {e}")
            return {}
    return {}

config = load_config()

QUALITY = config.get("quality", "worst")
TIMEOUT = config.get("timeout", 10)
MAX_WORKERS = config.get("max_workers", 10)
OUTPUT_FILE = config.get("output_file", "tiktok_live.m3u")
USERS_FILE = config.get("users_file", "userstiktok.txt")

GROUP_TITLE = config.get("group_title", "TikTok Live")
TVG_LOGO = config.get("tvg_logo", "https://www.tiktok.com/favicon.ico")
TVG_ID = config.get("tvg_id", "simpleTVFakeEpgId")
EXT_FILTER = config.get("ext_filter", "Tikitok live")

# Συνάρτηση φόρτωσης χρηστών από αρχείο
def load_users():
    users = []
    try:
        with open(USERS_FILE, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                users.append(line)
        print(f"Φορτώθηκαν {len(users)} χρήστες από το αρχείο {USERS_FILE}.")
    except FileNotFoundError:
        print(f"Το αρχείο {USERS_FILE} δεν βρέθηκε.")
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
    return users


# Συνάρτηση ελέγχου αν ο χρήστης είναι live
def check_user_live(user):
    try:
        result = subprocess.run(
            ["streamlink", f"https://www.tiktok.com/@{user}", QUALITY, "--stream-url"],
            capture_output=True, text=True, timeout=TIMEOUT
        )
        output = result.stdout.strip()
        
        if output.startswith("https://"):
            status = colored("είναι σε live", "yellow", "on_blue", attrs=["bold", "blink"])
            with open(OUTPUT_FILE, "a") as m3u_file:
                m3u_file.write(
                    f"#EXTINF:-1 group-title=\"{GROUP_TITLE}\" tvg-logo=\"{TVG_LOGO}\" "
                    f"tvg-id=\"{TVG_ID}\" $ExtFilter=\"{EXT_FILTER}\",{user}\n"
                )
                m3u_file.write(f"{output}\n")
            return f"Έλεγχος χρήστη: {user} - {status}"
        else:
            return f"Έλεγχος χρήστη: {user} - δεν είναι σε live"
    except Exception as e:
        return f"Σφάλμα κατά τον έλεγχο του χρήστη {user}: {e}"


# Φόρτωση χρηστών από το αρχείο
users = load_users()

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
with open(OUTPUT_FILE, "w") as m3u_file:
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

# Έλεγχος για κάθε χρήστη αν είναι live με παράλληλη εκτέλεση
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    results = list(
        tqdm(
            executor.map(check_user_live, users),
            total=len(users),
            desc="Έλεγχος χρηστών του tiktok",
            ncols=120,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}'
        )
    )
    for result in results:
        tqdm.write(result)

