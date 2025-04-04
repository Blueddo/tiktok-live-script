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

# Συνάρτηση για έλεγχο αν ο χρήστης είναι live
def check_user_live(user):
    result = subprocess.run(
        ["streamlink", f"https://www.tiktok.com/@{user}", "worst", "--stream-url"],
        capture_output=True, text=True
    )
    return result.stdout.strip()

# Συνάρτηση για διαχείριση των καθυστερήσεων και των σφαλμάτων IP Blocking
def manage_rate_limiting_and_ip_blocking(user, retries=3):
    for attempt in range(retries):
        output = check_user_live(user)
        
        if "error: No playable streams found on this URL" not in output:
            if output.startswith("https://"):
                return output, "είναι σε live"
        else:
            status = "δεν είναι σε live"
            return None, status
        
        # Έλεγχος για μηνύματα σφάλματος που σχετίζονται με IP Blocking
        if "error: Unable to open URL: 403 Client Error" in output:
            print(colored(f"Η IP έχει αποκλειστεί, αναμονή για 10 λεπτά πριν τον επόμενο έλεγχο...", "red"))
            time.sleep(600)  # Αναμονή για 10 λεπτά
        else:
            # Αναμονή για 10 δευτερόλεπτα μεταξύ των αιτημάτων για αποφυγή Rate Limiting
            time.sleep(10)
    print(colored(f"Αποτυχία να ελεγχθεί ο χρήστης {user} μετά από {retries} προσπάθειες.", "red"))
    return None, "αποτυχία ελέγχου"

# Φόρτωση χρηστών από το αρχείο
users = load_users()

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
with open("tiktok_live.m3u", "w") as m3u_file:
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

# Έλεγχος για κάθε χρήστη αν είναι live με μπάρα προόδου
for user in tqdm(users, desc="Έλεγχος χρηστών του TikTok", ncols=100):
    output, status = manage_rate_limiting_and_ip_blocking(user)
    
    if output:
        with open("tiktok_live.m3u", "a") as m3u_file:
            m3u_file.write(f"#EXTINF:-1 group-title=\"TikTok Live\" tvg-logo=\"https://www.tiktok.com/favicon.ico\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tikitok live\",{user}\n")
            m3u_file.write(f"{output}\n")
    
    tqdm.write(f"Έλεγχος χρήστη: {user} - {status}")

# Αφαίρεση μηνυμάτων σφάλματος από το αρχείο m3u
with open("tiktok_live.m3u", "r") as m3u_file:
    lines = m3u_file.readlines()

with open("tiktok_live.m3u", "w") as m3u_file:
    for line in lines:
        if not line.startswith("error:"):
            m3u_file.write(line)
