import concurrent.futures
import subprocess
from tqdm import tqdm
from termcolor import colored

# Συνάρτηση φόρτωσης χρηστών από αρχείο
def load_users():
    users = []
    try:
        with open("userstwitch.txt", "r") as file:
            for line in file:
                users.append(line.strip())
        print(f"Φορτώθηκαν {len(users)} χρήστες από το αρχείο userstwitch.txt.")
    except FileNotFoundError:
        print("Το αρχείο userstwitch.txt δεν βρέθηκε.")
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
    return users

# Συνάρτηση ελέγχου αν ο χρήστης είναι live
def check_user_live(user):
    try:
        result = subprocess.run(
            ["streamlink", f"https://www.twitch.tv/{user}", "720p", "--stream-url"],
            capture_output=True, text=True
        )
        output = result.stdout.strip()
        
        if output.startswith("https://"):
            status = colored("είναι σε live", "yellow", "on_blue", attrs=["bold", "blink"])
            with open("twitch_live.m3u", "a") as m3u_file:
                m3u_file.write(f"#EXTINF:-1 group-title=\"twitch Live\" tvg-logo=\"https://i.imgur.com/OQIOzbI.png\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Twitch live\",{user}\n")
                m3u_file.write(f"{output}\n")
            return f"Έλεγχος χρήστη: {user} - {status}"
        else:
            return f"Έλεγχος χρήστη: {user} - δεν υπάρχει διεύθυνση ροής"
    except Exception as e:
        return f"Σφάλμα κατά τον έλεγχο του χρήστη {user}: {e}"

# Φόρτωση χρηστών από το αρχείο
users = load_users()

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
with open("twitch_live.m3u", "w") as m3u_file:
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

# Έλεγχος για κάθε χρήστη αν είναι live με παράλληλη εκτέλεση
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(tqdm(executor.map(check_user_live, users), total=len(users), desc="Έλεγχος χρηστών του twitch", ncols=120, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}'))
    for result in results:
        tqdm.write(result)
