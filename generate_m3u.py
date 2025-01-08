import subprocess
import time
from tqdm import tqdm
from termcolor import colored

# Συνάρτηση φόρτωσης χρηστών από αρχείο
def load_users():
    users = []
    try:
        with open("userstiktok.txt", "r") as file:
            for line in file:
                users.append(line.strip())
        print(f"Φορτώθηκαν {len(users)} χρήστες από το αρχείο userstiktok.txt.")
    except FileNotFoundError:
        print("Το αρχείο userstiktok.txt δεν βρέθηκε.")
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
    return users

# Φόρτωση χρηστών από το αρχείο
users = load_users()

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
with open("tiktok_live.m3u", "w") as m3u_file:
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

# Έλεγχος για κάθε χρήστη αν είναι live με μπάρα προόδου
for user in tqdm(users, desc="Έλεγχος χρηστών του TikTok", ncols=100):
    result = subprocess.run(
        ["streamlink", f"https://www.tiktok.com/@{user}", "worst", "--stream-url"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    
    if "error: No playable streams found on this URL" not in output:
        if output.startswith("https://"):
            status = colored("είναι σε live", "yellow", "on_blue", attrs=["bold", "blink"])
            with open("tiktok_live.m3u", "a") as m3u_file:
                m3u_file.write(f"#EXTINF:-1 group-title=\"TikTok Live\" tvg-logo=\"https://www.tiktok.com/favicon.ico\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tikitok live\",{user}\n")
                m3u_file.write(f"{output}\n")
    else:
        status = "δεν είναι σε live"
    
    tqdm.write(f"Έλεγχος χρήστη: {user} - {status}")

# Αφαίρεση μηνυμάτων σφάλματος από το αρχείο m3u
with open("tiktok_live.m3u", "r") as m3u_file:
    lines = m3u_file.readlines()

with open("tiktok_live.m3u", "w") as m3u_file:
    for line in lines:
        if not line.startswith("error:"):
            m3u_file.write(line)
