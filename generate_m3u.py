import concurrent.futures
import subprocess
from tqdm import tqdm
from termcolor import colored

# Συνάρτηση φόρτωσης χρηστών από αρχείο
def load_users():
    try:
        with open("userstiktok.txt", "r") as file:
            users = [line.strip() for line in file if line.strip()]
        print(f"Φορτώθηκαν {len(users)} χρήστες από το αρχείο userstiktok.txt.")
        return users
    except FileNotFoundError:
        print("Το αρχείο userstiktok.txt δεν βρέθηκε.")
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
    return []

# Συνάρτηση ελέγχου αν ο χρήστης είναι live
def check_user_live(user):
    try:
        # Ζητάμε πρώτα worst και best σε μια κλήση
        result = subprocess.run(
            ["streamlink", f"https://www.tiktok.com/@{user}", "worst,best", "--stream-url"],
            capture_output=True, text=True
        )
        output = result.stdout.strip()

        if output:
            lines = output.splitlines()
            status = colored("είναι σε live", "yellow", "on_blue", attrs=["bold", "blink"])
            with open("tiktok_live.m3u", "a", encoding="utf-8") as m3u_file:
                for line in lines:
                    # Κάθε γραμμή περιέχει URL (streamlink επιστρέφει ποιότητα + URL μόνο αν δεν χρησιμοποιήσεις --stream-url ανά ποιότητα)
                    # Εδώ παίρνουμε με τη σειρά worst και best
                    m3u_file.write(
                        f"#EXTINF:-1 group-title=\"TikTok Live\" "
                        f"tvg-logo=\"https://www.tiktok.com/favicon.ico\" "
                        f"tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tiktok live\",{user}\n"
                    )
                    m3u_file.write(f"{line}\n")
            return f"Έλεγχος χρήστη: {user} - {status}"
        else:
            return f"Έλεγχος χρήστη: {user} - δεν είναι σε live"
    except Exception as e:
        return f"Σφάλμα κατά τον έλεγχο του χρήστη {user}: {e}"

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
with open("tiktok_live.m3u", "w", encoding="utf-8") as m3u_file:
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

users = load_users()

# Έλεγχος για κάθε χρήστη αν είναι live με παράλληλη εκτέλεση
with concurrent.futures.ThreadPoolExecutor() as executor:
    for result in tqdm(executor.map(check_user_live, users), total=len(users), desc="Έλεγχος χρηστών TikTok", ncols=120):
        tqdm.write(result)
