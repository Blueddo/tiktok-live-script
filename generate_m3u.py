import subprocess
import time
from tqdm import tqdm
from termcolor import colored

# Σταθερές για αναμονή
WAIT_TIME_BETWEEN_REQUESTS = 10  # σε δευτερόλεπτα
WAIT_TIME_IP_BLOCK = 600  # σε δευτερόλεπτα (10 λεπτά)

# Συνάρτηση φόρτωσης χρηστών από αρχείο
def load_users():
    users = set()  # Χρήση συνόλου για αποφυγή διπλοτύπων
    try:
        with open("userstiktok.txt", "r") as file:
            for line in file:
                users.add(line.strip())
        print(f"Φορτώθηκαν {len(users)} μοναδικοί χρήστες από το αρχείο userstiktok.txt.")
    except FileNotFoundError:
        print("Το αρχείο userstiktok.txt δεν βρέθηκε.")
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
    return list(users)  # Επιστροφή της λίστας των μοναδικών χρηστών

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
            print(colored(f"Η IP έχει αποκλειστεί, αναμονή για {WAIT_TIME_IP_BLOCK // 60} λεπτά πριν τον επόμενο έλεγχο...", "red"))
            time.sleep(WAIT_TIME_IP_BLOCK)
        else:
            # Αναμονή για 10 δευτερόλεπτα μεταξύ των αιτημάτων για αποφυγή Rate Limiting
            time.sleep(WAIT_TIME_BETWEEN_REQUESTS)
    print(colored(f"Αποτυχία να ελεγχθεί ο χρήστης {user} μετά από {retries} προσπάθειες.", "red"))
    return None, "αποτυχία ελέγχου"

# Φόρτωση χρηστών από το αρχείο
users = load_users()

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
m3u_lines = ["#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n"]

# Έλεγχος για κάθε χρήστη αν είναι live με μπάρα προόδου
for user in tqdm(users, desc="Έλεγχος χρηστών του TikTok", ncols=100):
    output, status = manage_rate_limiting_and_ip_blocking(user)
    
    if output:
        m3u_lines.append(f"#EXTINF:-1 group-title=\"TikTok Live\" tvg-logo=\"https://www.tiktok.com/favicon.ico\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tikitok live\",{user}\n")
        m3u_lines.append(f"{output}\n")
    
    tqdm.write(f"Έλεγχος χρήστη: {user} - {status}")

# Αφαίρεση μηνυμάτων σφάλματος από το αρχείο m3u
with open("tiktok_live.m3u", "w") as m3u_file:
    for line in m3u_lines:
        if not line.startswith("error:"):
            m3u_file.write(line)
