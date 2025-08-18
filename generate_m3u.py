import concurrent.futures
import subprocess
import threading
from tqdm import tqdm
from termcolor import colored

# Όνομα αρχείου M3U όπου θα σωθούν τα streams
M3U_PATH = "tiktok_live.m3u"

# Lock για να γράφουμε με ασφάλεια στο αρχείο από πολλά threads
file_lock = threading.Lock()

def load_users():
    """
    Διαβάζει το αρχείο userstiktok.txt και επιστρέφει λίστα με usernames.
    Αγνοεί κενές γραμμές και τυπώνει πόσοι χρήστες φορτώθηκαν.
    """
    try:
        with open("userstiktok.txt", "r", encoding="utf-8") as file:
            users = [line.strip() for line in file if line.strip()]
        print(f"Φορτώθηκαν {len(users)} χρήστες από το αρχείο userstiktok.txt.")
        return users
    except FileNotFoundError:
        print("Το αρχείο userstiktok.txt δεν βρέθηκε.")
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
    return []

def get_stream_url(user, quality):
    """
    Καλεί το streamlink για τον συγκεκριμένο χρήστη και ποιότητα (best ή worst)
    και επιστρέφει το direct URL του stream ή κενό string αν αποτύχει.
    """
    try:
        result = subprocess.run(
            ["streamlink", f"https://www.tiktok.com/@{user}", quality, "--stream-url"],
            capture_output=True, text=True
        )
        url = result.stdout.strip()
        return url if url.startswith("http") else ""
    except Exception:
        return ""

def write_m3u_entries(user, entries):
    """
    Γράφει στο M3U τις εγγραφές για τον χρήστη.
    entries = λίστα από tuples (label, url) π.χ. [("best", "..."), ("worst", "...")]
    """
    with file_lock:
        with open(M3U_PATH, "a", encoding="utf-8") as m3u:
            for label, url in entries:
                m3u.write(
                    f"#EXTINF:-1 group-title=\"TikTok Live\" "
                    f"tvg-logo=\"https://www.tiktok.com/favicon.ico\" "
                    f"tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tiktok live\",{user} [{label}]\n"
                )
                m3u.write(f"{url}\n")

def check_user_live(user):
    """
    Ελέγχει αν ο χρήστης είναι live.
    Αν είναι, γράφει πρώτα την 'best' και μετά την 'worst' ποιότητα (αν είναι διαφορετική).
    """
    try:
        # Ζητάμε πρώτα best και μετά worst
        best_url  = get_stream_url(user, "best")
        worst_url = get_stream_url(user, "worst")

        if not best_url and not worst_url:
            return f"Έλεγχος χρήστη: {user} - δεν είναι σε live"

        # Φτιάχνουμε λίστα εγγραφών με σειρά best → worst
        entries = []
        if best_url:
            entries.append(("best", best_url))
        if worst_url and worst_url != best_url:
            entries.append(("worst", worst_url))

        # Γράφουμε στο αρχείο M3U
        write_m3u_entries(user, entries)

        status = colored("είναι σε live", "yellow", "on_blue", attrs=["bold", "blink"])
        labels = ", ".join(label for label, _ in entries)
        return f"Έλεγχος χρήστη: {user} - {status} ({labels})"

    except Exception as e:
        return f"Σφάλμα κατά τον έλεγχο του χρήστη {user}: {e}"

if __name__ == "__main__":
    # Γράφουμε το header του M3U μία φορά στην αρχή
    with open(M3U_PATH, "w", encoding="utf-8") as m3u:
        m3u.write('#EXTM3U $BorpasFileFormat="1" $NestedGroupsSeparator="/"\n')

    # Φορτώνουμε χρήστες
    users = load_users()

    # Παράλληλη εκτέλεση ελέγχων
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for result in tqdm(
            executor.map(check_user_live, users),
            total=len(users),
            desc="Έλεγχος χρηστών TikTok",
            ncols=120
        ):
            tqdm.write(result)
