import os
import requests
import subprocess
from datetime import datetime, timedelta

# Μήνυμα έναρξης
print("==============================================================================================")
print("Καλώς ήρθατε στο Script Παρακολούθησης Ζωντανών Μεταδόσεων TikTok!")
print("Αυτό το script παρακολουθεί ζωντανές μεταδόσεις TikTok και δημιουργεί μια λίστα αναπαραγωγής m3u με τα URLs των ζωντανών ροών.")
print("Χρησιμοποιεί το streamlink για την εξαγωγή των URLs των ζωντανών ροών και ενημερώνει το αρχείο m3u.")
print("Παρέχει επίσης αυτόματη ενημέρωση και ανέβασμα του αρχείου m3u στο GitHub repository σας.")
print("Ας ξεκινήσουμε την παρακολούθηση...")
print("==============================================================================================")

def load_users():
    users = []
    try:
        with open("userstiktok.txt", "r") as file:
            for line in file:
                users.append(line.strip())
    except FileNotFoundError:
        print("Το αρχείο userstiktok.txt δεν βρέθηκε.")
    except Exception as e:
        print("Σφάλμα κατά την ανάγνωση του αρχείου:", e)
    return users

def check_user(user):
    result = subprocess.run(
        ["streamlink", f"https://www.tiktok.com/@{user}", "worst", "--stream-url"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()

    if output.startswith("https://pull-f5-tt03.fcdn.eu.tiktokcdn.com/stage/stream-"):
        start_time = datetime.now().strftime("%H:%M:%S")
        return user, output, start_time
    return user, None, None

def update_m3u_file(live_users):
    default_stream_url = "https://ak5.picdn.net/shutterstock/videos/1072225/preview/stock-footage-pretty-lady-watching-tv-with-popcorn-in-her-living-room.mp4"
    try:
        with open("tiktok_live.m3u", "w", encoding="utf-8") as m3u_file:
            write_m3u_header(m3u_file)
            if live_users:
                user_count = 0
                for user, (output, start_time) in live_users.items():
                    avatar_thumb = "https://www.tiktok.com/favicon.ico"
                    write_m3u_entry(m3u_file, avatar_thumb, user, start_time, output)
                    user_count += 1
                print(f"Το αρχείο M3U ενημερώθηκε επιτυχώς με τον χρήστη {user}. Συνολικά: {user_count} live.")
            else:
                write_default_stream(m3u_file, default_stream_url)
                print("Το αρχείο M3U ενημερώθηκε επιτυχώς.")
    except Exception as e:
        print(f"Σφάλμα κατά την ενημέρωση του αρχείου m3u: {e}")
        with open("tiktok_live.m3u", "w", encoding="utf-8") as m3u_file:
            write_m3u_header(m3u_file)
            write_default_stream(m3u_file, default_stream_url)
        print("Προστέθηκε το προεπιλεγμένο stream λόγω σφάλματος.")

def write_m3u_header(m3u_file):
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

def write_m3u_entry(m3u_file, avatar_thumb, user, start_time, output):
    m3u_file.write(f"#EXTINF:-1 group-title=\"TikTok Live\" tvg-logo=\"{avatar_thumb}\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tikitok live\",{user}\n")
    m3u_file.write(f"{output}\n")

def write_default_stream(m3u_file, default_stream_url):
    m3u_file.write("#EXTINF:-1 group-title=\"TikTok Live\" tvg-logo=\"https://www.tiktok.com/favicon.ico\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tikitok live\",Default Stream\n")
    m3u_file.write(f"{default_stream_url}\n")

def push_to_github():
    if os.path.exists("tiktok_live.m3u"):
        try:
            # Configure Git user with a no-reply email
            subprocess.run(["git", "config", "--global", "user.email", "Blueddo@users.noreply.github.com"], check=True)
            subprocess.run(["git", "config", "--global", "user.name", "Blueddo"], check=True)

            # Add changes to git
            subprocess.run(["git", "add", "tiktok_live.m3u"], check=True)
            subprocess.run(["git", "commit", "-m", "Update tiktok_live.m3u"], check=True)

            # Push changes to GitHub using PAT
            subprocess.run(["git", "push", "https://Blueddo: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@github.com/Blueddo/tiktok-live-script.git"], check=True)
            print("Αλλαγές ανέβηκαν στο GitHub.")
        except subprocess.CalledProcessError as e:
            print(f"Σφάλμα κατά την προώθηση αλλαγών στο GitHub: {e}")

def fetch_and_save_data():
    users = load_users()
    live_users = {}

    for user in users:
        user, output, start_time = check_user(user)
        if output:
            live_users
    update_m3u_file(live_users)
    push_to_github()