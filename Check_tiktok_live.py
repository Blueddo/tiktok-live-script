import requests
import json
import subprocess
from datetime import datetime, timedelta

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
    profile_data = load_profile_data()
    default_stream_url = "https://ak5.picdn.net/shutterstock/videos/1072225/preview/stock-footage-pretty-lady-watching-tv-with-popcorn-in-her-living-room.mp4"
    try:
        with open("tiktok_live.m3u", "w", encoding="utf-8") as m3u_file:
            write_m3u_header(m3u_file)
            if live_users:
                user_count = 0
                for user, (output, start_time) in live_users.items():
                    avatar_thumb = get_avatar_thumb(user, profile_data)
                    if not check_image_access(avatar_thumb):
                        avatar_thumb = "https://www.tiktok.com/favicon.ico"
                    try:
                        short_avatar_thumb = shorten_url(avatar_thumb)
                    except Exception as e:
                        print(f"Σφάλμα κατά την συντόμευση της διεύθυνσης URL: {e}")
                        short_avatar_thumb = avatar_thumb
                    if short_avatar_thumb is None:
                        short_avatar_thumb = avatar_thumb
                    write_m3u_entry(m3u_file, short_avatar_thumb, user, start_time, output)
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

def write_m3u_entry(m3u_file, short_avatar_thumb, user, start_time, output):
    m3u_file.write(f"#EXTINF:-1 group-title=\"TikTok Live\" tvg-logo=\"{short_avatar_thumb}\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tikitok live\",{user}\n")
    m3u_file.write(f"{output}\n")

def write_default_stream(m3u_file, default_stream_url):
    m3u_file.write("#EXTINF:-1 group-title=\"TikTok Live\" tvg-logo=\"https://www.tiktok.com/favicon.ico\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tikitok live\",Default Stream\n")
    m3u_file.write(f"{default_stream_url}\n")

def get_avatar_thumb(user, profile_data):
    for profile in profile_data:
        if profile.get("user", {}).get("uniqueId") == user:
            avatar_thumb = profile.get("user", {}).get("avatarThumb", "https://www.tiktok.com/favicon.ico")
            if check_image_access(avatar_thumb):
                return avatar_thumb
    return "https://www.tiktok.com/favicon.ico"

def check_image_access(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Βεβαιωθείτε ότι το αίτημα ήταν επιτυχές
        return True
    except requests.RequestException:
        return False

def fetch_and_save_data():
    users = load_users()
    live_users = {}

    for user in users:
        user, output, start_time = check_user(user)
        if output:
            live_users