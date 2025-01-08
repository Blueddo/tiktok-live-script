# Μήνυμα έναρξης
print("==========================================================================================================")
print("🥳 Καλώς ήρθατε στο Script Παρακολούθησης των live απο TikTok! 🥳")
print("----------------------------------------------------------------------------------------------------------")
print("Αυτό το script παρακολουθεί τα live απο TikTok και δημιουργεί μια λίστα αναπαραγωγής m3u με τα URLs των live.")
print("Χρησιμοποιεί το streamlink για την εξαγωγή των URLs των live και ενημερώνει το αρχείο m3u.")
print("Ας ξεκινήσουμε την παρακολούθηση...")
print("==========================================================================================================")

# Βιβλιοθήκες για παράλληλη εκτέλεση και διαχείριση χρόνου
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import requests
import os
import re
import logging
import json
import subprocess
import time
import validators
import pyshorteners

# Φόρτωση χρηστών από αρχείο
def load_users():
    users = []
    try:
        with open("userstiktok.txt", "r") as file:
            for line in file:
                users.append(line.strip())
    except FileNotFoundError:
        print("Το αρχείο userstiktok.txt δεν βρέθηκε.")
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
    return users

# Έλεγχος εγκυρότητας URL
def is_valid_url(url):
    return validators.url(url)

# Συντόμευση URL
def shorten_url(url: str) -> str:
    if not validators.url(url):
        raise ValueError("Το URL δεν είναι έγκυρο.")
    
    if url in url_cache:
        return url_cache[url]
    
    if not settings['general_settings']['url_shortening_enabled']:
        return url
     # Ελέγχει αν η διεύθυνση URL είναι ήδη σύντομη (π.χ. εικονίδιο)   
    if "favicon.ico" in url or len(url) < 30:
        return url

    shortening_service = settings['general_settings']['url_shortening_service']

    try:
        if shortening_service == 'tinyurl':
            response = requests.get(f'http://tinyurl.com/api-create.php?url={url}', timeout=10)
        elif shortening_service == 'isgd':
            response = requests.get(f'https://is.gd/create.php?format=simple&url={url}', timeout=10)
        else:
            raise ValueError(f"Άγνωστη υπηρεσία συντόμευσης URL: {shortening_service}")
        
        response.raise_for_status()
        short_url = response.text
        url_cache[url] = short_url
        return short_url
    except Exception as e:
        logging.error(f"Σφάλμα κατά την συντόμευση της διεύθυνσης URL με την υπηρεσία {shortening_service}: {e}")
        return url  # Επιστρέφουμε την αρχική διεύθυνση URL σε περίπτωση αποτυχίας.

# Έλεγχος χρήστη για live
def check_user(user):
    result = subprocess.run(
        ["streamlink", "--stream-url", f"https://www.tiktok.com/@{user}", "best"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    
    if output.startswith("https://"):
        start_time = datetime.now().strftime("%H:%M:%S")
        return user, output, start_time
    return user, None, None

# Έλεγχος χρηστών για live
def check_live_users():
    global running, active_live_count
    running = True
    live_users = {}
    previous_live_users = {}
    users = load_users()
    
    while running:
        current_live_users = {}
        print("Ξεκινάει ο έλεγχος των χρηστών για αναζήτηση live...")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(check_user, user): user for user in users}
            for future in as_completed(futures):
                user, output, start_time = future.result()
                if output:
                    current_live_users[user] = (output, start_time)
                    if user not in previous_live_users:
                        previous_live_users[user] = start_time
                        with open("live_history_tiktok.log", "a", encoding="utf-8") as log_file:
                            formatted_date = datetime.now().strftime("%A, %d %B %Y - %H:%M:%S")
                            log_file.write(f"{formatted_date} - {user} - βρέθηκε live\n")
                        live_users[user] = (output, start_time)
                        update_m3u_file(live_users)
                    else:
                        live_users[user] = (output, previous_live_users[user])
                else:
                    if user in previous_live_users:
                        with open("live_history_tiktok.log", "a", encoding="utf-8") as log_file:
                            formatted_date = datetime.now().strftime("%A, %d %B %Y - %H:%M:%S")
                            log_file.write(f"{formatted_date} - {user} - σταμάτησε το live\n")
                        del previous_live_users[user]
        live_users = current_live_users
        print("Ο έλεγχος ολοκληρώθηκε. Αναμονή για τον επόμενο κύκλο...")
        time.sleep(loop_interval * 60)

# Ενημέρωση αρχείου M3U
def update_m3u_file(live_users):
    profile_data = load_profile_data()
    default_stream_url = settings['general_settings']['default_stream_url']
    
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
                        logging.error(f"Σφάλμα κατά την συντόμευση της διεύθυνσης URL: {e}")
                        short_avatar_thumb = avatar_thumb
                    
                    if short_avatar_thumb is None:
                        short_avatar_thumb = avatar_thumb
                    
                    write_m3u_entry(m3u_file, short_avatar_thumb, user, start_time, output)
                    user_count += 1
                logging.info(f"Το αρχείο M3U ενημερώθηκε επιτυχώς με {user_count} live χρήστες.")
            else:
                write_default_stream(m3u_file, default_stream_url)
                logging.info("Το αρχείο M3U ενημερώθηκε επιτυχώς με το προεπιλεγμένο stream.")
    except Exception as e:
        logging.error(f"Σφάλμα κατά την ενημέρωση του αρχείου m3u: {e}")
        with open("tiktok_live.m3u", "w", encoding="utf-8") as m3u_file:
            write_m3u_header(m3u_file)
            write_default_stream(m3u_file, default_stream_url)

# Γράψιμο κεφαλίδας M3U
def write_m3u_header(m3u_file):
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

# Γράψιμο εγγραφής M3U
def write_m3u_entry(m3u_file, short_avatar_thumb, user, start_time, output):
    group_title = settings['general_settings']['group_title']
    tvg_id = settings['general_settings']['tvg_id']
    m3u_file.write(f"#EXTINF:-1 group-title=\"{group_title}\" tvg-logo=\"{short_avatar_thumb}\" tvg-id=\"{tvg_id}\" $ExtFilter=\"Tikitok live\",{user}\n")
    m3u_file.write(f"{output}\n")

# Γράψιμο προεπιλεγμένου stream M3U
def write_default_stream(m3u_file, default_stream_url):
    group_title = settings['general_settings']['group_title']
    tvg_id = settings['general_settings']['tvg_id']
    m3u_file.write(f"#EXTINF:-1 group-title=\"{group_title}\" tvg-logo=\"https://www.tiktok.com/favicon.ico\" tvg-id=\"{tvg_id}\" $ExtFilter=\"Tikitok live\",Default Stream\n")
    m3u_file.write(f"{default_stream_url}\n")

# Λήψη avatar χρήστη
def get_avatar_thumb(user, profile_data):
    for profile in profile_data:
        if profile.get("user", {}).get("uniqueId") == user:
            avatar_thumb = profile.get("user", {}).get("avatarThumb", "https://www.tiktok.com/favicon.ico")
            if check_image_access(avatar_thumb):
                return avatar_thumb
    return "https://www.tiktok.com/favicon.ico"

# Έλεγχος πρόσβασης εικόνας
def check_image_access(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

# Φόρτωση δεδομένων προφίλ
def load_profile_data():
    try:
        with open("profile_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Το αρχείο δεδομένων προφίλ δεν βρέθηκε.")
        return []
    except json.JSONDecodeError:
        print("Σφάλμα στην αποκωδικοποίηση των δεδομένων προφίλ.")
        return []
    except Exception as e:
        print(f"Σφάλμα κατά την φόρτωση των δεδομένων προφίλ: {e}")
        return []

# Κύρια συνάρτηση
def main():
    global settings, url_cache, loop_interval
    settings = {
        'general_settings': {
            'default_stream_url': 'http://defaultstream.com',
            'url_shortening_enabled': True,
            'url_shortening_service': 'tinyurl',
            'group_title': 'Tikitok live',
            'tvg_id': 'TikitokLive'
        }
    }
    url_cache = {}
    loop_interval = 1  # Μπορείς να το αλλάξεις σε ό,τι διάστημα θες σε λεπτά
    check_live_users()

if __name__ == "__main__":
    main()
