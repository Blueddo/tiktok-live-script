import subprocess
import os

# Διαδρομή του repository στο περιβάλλον του GitHub Actions
repo_path = "/home/runner/work/tiktok-live-script/tiktok-live-script"

# Συνάρτηση για να διαβάσει τους χρήστες από το αρχείο userstiktok.txt
def read_users_from_file(file_path):
    with open(file_path, "r") as file:
        users = [line.strip() for line in file if line.strip()]
    return users

# Διαβάζουμε τους χρήστες από το αρχείο userstiktok.txt
users_file_path = os.path.join(repo_path, "userstiktok.txt")
users = read_users_from_file(users_file_path)

# Αφαίρεση διπλότυπων χρηστών
users = list(set(users))
print("Η λίστα των χρηστών χωρίς διπλότυπα δημιουργήθηκε")

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
m3u_filename = "tiktok_live.m3u"
m3u_filepath = os.path.join(repo_path, m3u_filename)
with open(m3u_filepath, "w") as m3u_file:
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")
print("Δημιουργήθηκε το αρχείο m3u και γράφτηκε η επικεφαλίδα")

def check_user(user):
    result = subprocess.run(
        ["streamlink", "https://www.tiktok.com/@{}".format(user), "worst", "--stream-url"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    
    if output.startswith("https://pull-f5-tt03.fcdn.eu.tiktokcdn.com/stage/stream-"):
        return user, output
    return user, None

# Έλεγχος για κάθε χρήστη αν είναι live
any_live_stream = False  # Σημαία για να ελέγξει αν υπάρχει κάποιο live stream
for idx, user in enumerate(users, start=1):
    print(f"Έλεγχος {idx} για τον χρήστη: {user}")
    user, output = check_user(user)
    
    if output:
        with open(m3u_filepath, "a") as m3u_file:
            m3u_file.write(f"#EXTINF:-1 group-title=\"TikTok Live\" tvg-logo=\"https://www.tiktok.com/favicon.ico\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tikitok live\",{user}\n")
            m3u_file.write(f"{output}\n")
        print(f"Ο χρήστης {user} είναι live και προστέθηκε στο αρχείο m3u.")
        any_live_stream = True  # Ενημέρωση της σημαίας αν βρεθεί κάποιο live stream
    else:
        print(f"Ο χρήστης {user} δεν είναι live.")

# Προσθήκη καταγραφής
if any_live_stream:
    print("Το αρχείο m3u ενημερώθηκε με νέα δεδομένα.")
else:
    print("Το αρχείο m3u δεν ενημερώθηκε με νέα δεδομένα.")
