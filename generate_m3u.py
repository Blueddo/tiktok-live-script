# Μήνυμα έναρξης
print("==========================================================================================================")
print("🥳 Καλώς ήρθατε στο Script Παρακολούθησης των live απο TikTok! 🥳")
print("----------------------------------------------------------------------------------------------------------")
print("Αυτό το script παρακολουθεί τα live απο TikTok και δημιουργεί μια λίστα αναπαραγωγής m3u με τα URLs των live.")
print("Χρησιμοποιεί το streamlink για την εξαγωγή των URLs των live και ενημερώνει το αρχείο m3u.")
print("Ας ξεκινήσουμε την παρακολούθηση...")
print("==========================================================================================================")
# Βιβλιοθήκες για το γραφικό περιβάλλον:
import tkinter as tk  # Εισάγει το κύριο module του Tkinter για τη δημιουργία γραφικών διεπαφών χρήστη (GUI).
from tkinter import filedialog, Toplevel, messagebox, Listbox, ttk  # Εισάγει συγκεκριμένα widgets και διαλόγους του Tkinter.
import customtkinter as ctk  # Χρησιμοποιείται για την κατασκευή Custom Tkinter GUI.
from CTkListbox import CTkListbox  # Χρησιμοποιείται για τη δημιουργία λίστας στο Custom Tkinter.
from PIL import Image, ImageTk  # Εισάγει το Pillow για επεξεργασία εικόνων και τη χρήση τους σε Tkinter.
# Βιβλιοθήκες για προσαρμοσμένη διεπαφή και στατιστικά:
from alive_progress import alive_bar  # Εισάγει τη βιβλιοθήκη alive_progress για τη δημιουργία progress bars στο terminal.
from termcolor import colored  # Εισάγει τη βιβλιοθήκη termcolor για χρωματισμό κειμένου στο terminal.
from colorama import Fore, Style, init  # Χρησιμοποιείται για χρωματισμό κειμένου στην κονσόλα.
# Βιβλιοθήκες για παράλληλη εκτέλεση και διαχείριση χρόνου:
from concurrent.futures import ThreadPoolExecutor, as_completed  # Εισάγει εργαλεία για παράλληλη εκτέλεση εργασιών με threads.
from datetime import datetime, timedelta  # Εισάγει εργαλεία για διαχείριση ημερομηνιών και χρόνου.
from babel.dates import format_datetime  # Εισάγει τη βιβλιοθήκη Babel για μορφοποίηση ημερομηνιών και χρόνου σύμφωνα με τοπικές ρυθμίσεις.
from dateutil import parser  # Εισαγωγή της συνάρτησης parser από τη βιβλιοθήκη dateutil για την ανάλυση (parsing) ημερομηνιών
# Βιβλιοθήκες για τη διαχείριση αρχείων και HTTP αιτήσεις:
import requests  # Εισάγει τη βιβλιοθήκη requests για HTTP αιτήσεις.
import os  # Παρέχει λειτουργίες για την αλληλεπίδραση με το λειτουργικό σύστημα.
import re  # Χρησιμοποιείται για κανονικές εκφράσεις και ανάλυση κειμένου.
import logging  # Χρησιμοποιείται για καταγραφή μηνυμάτων καταγραφής (logs).
import csv  # Εισάγει το csv για ανάγνωση και εγγραφή αρχείων CSV.
import json  # Εισάγει το json για διαχείριση δεδομένων σε μορφή JSON.
import io  # Εισάγει το module io για διαχείριση ροών δεδομένων (streams).
import mmap  # Εισάγει το mmap για διαχείριση μνήμης μέσω memory-mapped files.
# Βιβλιοθήκες για συστήματα και threads:
import ctypes  # Εισάγει το ctypes για κλήσεις σε C βιβλιοθήκες.
import threading  # Εισάγει το threading για δημιουργία και διαχείριση threads.
import subprocess  # Εισάγει το subprocess για εκτέλεση εξωτερικών διεργασιών.
import time  # Εισάγει το time για λειτουργίες σχετικές με τον χρόνο.
import locale  # Εισάγει το locale για διαχείριση τοπικών ρυθμίσεων.
# Άλλες χρήσιμες βιβλιοθήκες:
from fpdf import FPDF  # Χρησιμοποιείται για τη δημιουργία αρχείων PDF.
import validators  # Εισάγει τη βιβλιοθήκη validators για έλεγχο εγκυρότητας δεδομένων (π.χ. URLs).
import pyshorteners  # Εισάγει το pyshorteners για συντόμευση URLs.

# Ρυθμίζει το logging για την καταγραφή μηνυμάτων σε επίπεδο INFO
logging.basicConfig(level=logging.INFO, format='%(message)s - %(levelname)s - %(funcName)s')
settings = {}

# Ρυθμίσεις από το αρχείο settings.json
sound_enabled = settings.get("general_settings", {}).get("sound_enabled", True)  # Ενεργοποιεί ή απενεργοποιεί τον ήχο ειδοποίησης.
loop_enabled = settings.get("general_settings", {}).get("loop_enabled", True)  # Ενεργοποιεί ή απενεργοποιεί την επαναλαμβανόμενη λειτουργία.
alert_sound = settings.get("general_settings", {}).get("alert_sound", "alert.wav")  # Ορίζει το αρχείο ήχου που θα αναπαράγεται για ειδοποιήσεις.
loop_interval = settings.get("general_settings", {}).get("loop_interval", 120)  # Διάστημα επανάληψης σε δευτερολεπτα
countdown_interval = settings.get("general_settings", {}).get("countdown_interval", 60)
minutes_var = settings.get("general_settings", {}).get("search_interval", "1")

# Γενικές μεταβλητές
countdown_active = False  # Καθορίζει αν η αντίστροφη μέτρηση είναι ενεργή ή όχι.
alert_sound = "alert.wav"  # Αρχείο ήχου που θα αναπαράγεται κατά την ειδοποίηση.
unique_users = set()  # Σύνολο για την αποθήκευση μοναδικών χρηστών.
printed_lines = set()  # Σύνολο για την αποθήκευση των εκτυπωμένων μηνυμάτων, εξασφαλίζοντας ότι τα μηνύματα δεν θα εκτυπωθούν περισσότερες από μία φορές.
notified_users = set()  # Σύνολο για την αποθήκευση των χρηστών που έχουν ειδοποιηθεί.
live_stats = {}  # Λεξικό για την αποθήκευση στατιστικών στοιχείων των live.
previous_live_users = {}  # Λεξικό για την αποθήκευση των χρηστών που ήταν live στον προηγούμενο έλεγχο.
live_users = {}  # Λεξικό για την αποθήκευση των τρέχοντων χρηστών που είναι live.
last_live_links = {}  # Λεξικό για την αποθήκευση των τελευταίων συνδέσμων live των χρηστών.
countdown_event = threading.Event()  # Συγχρονιστικό γεγονός για την αντίστροφη μέτρηση, επιτρέποντας την αλληλεπίδραση με νήματα.
url_cache = {}  # Λεξικό για την αποθήκευση της προσωρινής μνήμης των URL, για να αποφευχθεί η πολλαπλή πρόσβαση στα ίδια δεδομένα.

def print_once(message):
    if message not in printed_lines:
        print(message)
        printed_lines.add(message)

# Φόρτωση προεπιλεγμένων ρυθμίσεων από το αρχείο default_settings.json
def load_default_settings():
    try:
        with open("default_settings.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Το αρχείο default_settings.json δεν βρέθηκε.")
        return {}
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου default_settings.json: {e}")
        return {}

# Εξασφάλιση ότι οι προεπιλεγμένες ρυθμίσεις υπάρχουν στο settings
def ensure_default_settings():
    default_settings = load_default_settings()
    # Εξασφάλιση ότι υπάρχουν οι βασικές ρυθμίσεις
    if 'general_settings' not in settings:
        settings['general_settings'] = {}
    if 'profile_settings' not in settings:
        settings['profile_settings'] = {}
    if 'window_positions' not in settings:
        settings['window_positions'] = {}

    # Προσθήκη προεπιλεγμένων ρυθμίσεων αν λείπουν
    settings['general_settings'] = {**default_settings.get('general_settings', {}), **settings.get('general_settings', {})}
    settings['profile_settings'] = {**default_settings.get('profile_settings', {}), **settings.get('profile_settings', {})}
    settings['window_positions'] = {**default_settings.get('window_positions', {}), **settings.get('window_positions', {})}

def load_settings():
    global settings
    try:
        with open("settings.json", "r", encoding="utf-8") as file:
            settings = json.load(file)
        print(f"Οι ρυθμίσεις φορτώθηκαν επιτυχώς. Συνολικός αριθμός ρυθμίσεων: {len(settings)}")
    except FileNotFoundError:
        print("Το αρχείο settings.json δεν βρέθηκε.")
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου settings.json: {e}")

def save_settings():
    global settings
    try:
        with open("settings.json", "w", encoding="utf-8") as file:
            json.dump(settings, file, ensure_ascii=False, indent=4)
        print_once("Οι ρυθμίσεις αποθηκεύτηκαν επιτυχώς.")
    except Exception as e:
        print(f"Σφάλμα κατά την αποθήκευση του αρχείου settings.json: {e}")

def apply_settings():
    global settings
    root.configure(bg=settings['general_settings']['background_color'])
    root.attributes("-topmost", settings['general_settings']['always_on_top'])

def watch_settings_file():
    import time
    last_modified_time = os.path.getmtime("settings.json")
    while True:
        current_modified_time = os.path.getmtime("settings.json")
        if current_modified_time != last_modified_time:
            last_modified_time = current_modified_time
            load_settings()
            apply_settings()
            print("Οι ρυθμίσεις ενημερώθηκαν.")
        time.sleep(1)
        
def load_profile_data():
    try:
        with open("profile_data.json", "r", encoding="utf-8") as file:  # Ανοίγει το αρχείο profile_data.json για ανάγνωση.
            return json.load(file)  # Φορτώνει τα δεδομένα JSON από το αρχείο και τα επιστρέφει.
    except FileNotFoundError:
        messagebox.showerror("Σφάλμα", "Το αρχείο δεδομένων προφίλ δεν βρέθηκε.")  # Εμφανίζει μήνυμα σφάλματος αν το αρχείο δεν βρεθεί.
        return []
    except json.JSONDecodeError:
        messagebox.showerror("Σφάλμα", "Σφάλμα στην αποκωδικοποίηση του JSON από το αρχείο δεδομένων προφίλ.")  # Εμφανίζει μήνυμα σφάλματος αν υπάρχει πρόβλημα στην αποκωδικοποίηση του JSON.
        return []
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατή η φόρτωση των δεδομένων προφίλ: {e}")  # Εμφανίζει μήνυμα σφάλματος για οποιοδήποτε άλλο σφάλμα.
        return []

profile_data = load_profile_data()  # Φορτώνει τα δεδομένα προφίλ κατά την εκκίνηση.
current_popup = None  # Αρχικοποιεί την μεταβλητή για το τρέχον αναδυόμενο παράθυρο.

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

def main():
    profile_data = load_profile_data()
    users = load_users()
    print(f"Συνολικός αριθμός χρηστών: {len(users)}")
    print(f"Συνολικός αριθμός δεδομένων προφίλ: {len(profile_data)}")

if __name__ == "__main__":
    main()

# Συνάρτηση για την ενεργοποίηση/απενεργοποίηση του "always on top"
def toggle_always_on_top():
    global root, settings
    always_on_top = not settings['general_settings']['always_on_top']
    root.attributes("-topmost", always_on_top)
    settings['general_settings']['always_on_top'] = always_on_top
    save_settings()
    print(f"Always on Top: {always_on_top}")

def load_live_history():
    live_stats = {}
    with open("live_history_tiktok.log", "r", encoding="utf-8") as log_file:
        lines = log_file.readlines()
        for line in lines:
            match_start = re.match(r"(.+?) - (.+?) - βρέθηκε live", line)
            match_end = re.match(r"(.+?) - (.+?) - σταμάτησε το live", line)

            if match_start:
                date_str, user, start_time_str = match_start.groups()
                start_time = datetime.strptime(f"{date_str} {start_time_str}", "%A, %d %B %Y - %H:%M:%S")
                if user not in live_stats:
                    live_stats
        
def get_live_history(username):
    history = []
    try:
        with open("live_history_tiktok.log", "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()
            for line in reversed(lines):
                if username in line:
                    history.append(line.strip())
    except FileNotFoundError:
        return ["Δεν βρέθηκε ιστορικό live."]
    return history if history else ["Δεν βρέθηκε ιστορικό live."]
    
def get_live_history_from_log(username):
    live_history = []
    with open("live_history_tiktok.log", "r", encoding="utf-8") as log_file:
        for line in log_file:
            if username in line:
                live_history.append(line.strip())
    return live_history

def extract_duration(line):
    try:
        parts = line.split()
        for part in parts:
            if part.isdigit():
                return int(part)
    except ValueError as e:
        print(f"Σφάλμα κατά την εξαγωγή της διάρκειας: {e}")
    return 0  # Επιστροφή 0 αν δεν βρεθεί κανένας αριθμός ή αν υπάρξει σφάλμα

def count_proxies(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            proxies = file.readlines()
        return len(proxies)
    except FileNotFoundError:
        return 0
    
def count_comments(comments_file):
    total = positive = negative = neutral = positive_stars = negative_stars = neutral_stars = total_stars = 0
    try:
        with open(comments_file, 'r', encoding='utf-8') as file:
            for line in file:
                total += 1
                if 'Κατηγορία: Θετικό' in line:
                    positive += 1
                    match = re.search(r'\((\d) star', line)
                    if match:
                        positive_stars += int(match.group(1))
                elif 'Κατηγορία: Αρνητικό' in line:
                    negative += 1
                    match = re.search(r'\((\d) star', line)
                    if match:
                        negative_stars += int(match.group(1))
                elif 'Κατηγορία: Ουδέτερο' in line:
                    neutral += 1
                    match = re.search(r'\((\d) star', line)
                    if match:
                        neutral_stars += int(match.group(1))
    except Exception as e:
        print(f"Σφάλμα κατά την ανάλυση των σχολίων: {e}")
        raise ValueError(e)
    
    total_stars = positive_stars + negative_stars + neutral_stars
    return total, positive, negative, neutral, positive_stars, negative_stars, neutral_stars, total_stars

def translate_greek_to_english(date_str):
    translations = {
        "Δευτέρα": "Monday", "Τρίτη": "Tuesday", "Τετάρτη": "Wednesday", "Πέμπτη": "Thursday",
        "Παρασκευή": "Friday", "Σάββατο": "Saturday", "Κυριακή": "Sunday",
        "Ιανουαρίου": "January", "Φεβρουαρίου": "February", "Μαρτίου": "March", "Απριλίου": "April",
        "Μαΐου": "May", "Ιουνίου": "June", "Ιουλίου": "July", "Αυγούστου": "August",
        "Σεπτεμβρίου": "September", "Οκτωβρίου": "October", "Νοεμβρίου": "November", "Δεκεμβρίου": "December"
    }
    for gr, en in translations.items():
        date_str = date_str.replace(gr, en)
    return date_str

def parse_date(date_str):
    translated_timestamp_str = translate_greek_to_english(date_str)
    try:
        return parser.parse(translated_timestamp_str)
    except Exception as e:
        print(f"Σφάλμα κατά την ανάλυση της γραμμής: {e}")
        return None

def parse_log_line(line):
    match = re.search(r"(.+) - (.+) - (.+)", line)
    if match:
        timestamp_str = match.group(1).strip()
        username = match.group(2).strip()
        action = match.group(3).strip()
        timestamp = parse_date(timestamp_str)
        return timestamp, username, action
    return None, None, None

def get_live_durations(live_history, live_users, username):
    durations = []
    total_duration = 0
    current_start = None
    last_timestamp = None
    last_check_time = datetime.now()  # Πρόσθεσε τον τελευταίο έλεγχο χρόνου

    for line in live_history:
        timestamp, log_username, action = parse_log_line(line)
        if log_username != username:
            continue

        if action == 'βρέθηκε live':
            current_start = timestamp
        elif action == 'σταμάτησε το live':
            if current_start:
                duration = (timestamp - current_start).total_seconds()
                durations.append(duration)
                total_duration += duration
                current_start = None

        last_timestamp = timestamp

    if current_start:  # Αν υπάρχει ένα ανοιχτό διάστημα, υπολόγισε το μέχρι την τρέχουσα ώρα ή τον τελευταίο έλεγχο
        if username in live_users:
            last_check_time = datetime.strptime(live_users[username][1], "%H:%M:%S")
        else:
            last_check_time = datetime.now()
        duration = (last_check_time - current_start).total_seconds() / 60
        durations.append(duration)
        total_duration += duration

    return durations, total_duration

def format_duration(total_minutes):
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    seconds = int((total_minutes * 60) % 60)
    return f"{hours} ώρες, {minutes} λεπτά, {seconds} δευτ."

def save_live_state(live_users):
    with open("live_state.json", "w", encoding="utf-8") as file:
        json.dump(live_users, file)

def load_live_state():
    try:
        with open("live_state.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

live_users = load_live_state()

# Κάθε φορά που αλλάζει η κατάσταση, αποθήκευσε τη νέα κατάσταση
def update_live_state(user, live_users):
    live_users
# Σώσε την κατάσταση των live users τακτικά ή σε συγκεκριμένα σημεία στον κώδικά σου
save_live_state(live_users)

# Δημιουργία του μενού χρηστών
def open_user_menu():
    users = load_users()
    menu = tk.Menu(root, tearoff=0, font=("Helvetica", 14), fg='white', bg='black')
    for user in users:
        menu.add_command(label=user, command=lambda u=user: show_profile_info(u))
    menu.post(root.winfo_pointerx(), root.winfo_pointery())

def show_profile_info(username):
    global current_popup
    if current_popup is not None and str(current_popup) != "":
        save_window_position(current_popup, f"profile_{username}")
        current_popup.destroy()
    user_data = next((item for item in profile_data if item['user']['uniqueId'] == username), {})
    if not user_data:
        print(f"Σφάλμα: Δεν βρέθηκαν δεδομένα για τον χρήστη {username}")
        return
    user_info = user_data.get("user", {})
    stats_info = user_data.get("stats", {})
    info_text = ""
    if user_info.get('uniqueId'):
        info_text += f"Όνομα χρήστη: {user_info.get('uniqueId')}\n"
    if user_info.get('nickname'):
        info_text += f"Ψευδώνυμο: {user_info.get('nickname')}\n"
    if user_info.get('signature'):
        info_text += f"Περιγραφή: {user_info.get('signature')}\n"
    if user_info.get('createTime'):
        try:
            create_time = datetime.fromtimestamp(user_info['createTime'])
            formatted_create_time = format_datetime(create_time, "EEEE, d MMMM y - HH:mm:ss", locale='el')
            info_text += f"Ημερομηνία Δημιουργίας: {formatted_create_time}\n"
        except Exception as e:
            info_text += f"Σφάλμα κατά την μετατροπή της ημερομηνίας δημιουργίας: {e}\n"
    if user_info.get('uniqueIdModifyTime'):
        try:
            unique_id_modify_time = datetime.fromtimestamp(user_info['uniqueIdModifyTime'])
            formatted_unique_id_modify_time = format_datetime(unique_id_modify_time, "EEEE, d MMMM y - HH:mm:ss", locale='el')
            info_text += f"Ημερομηνία Αλλαγής Ονόματος Χρήστη: {formatted_unique_id_modify_time}\n"
        except Exception as e:
            info_text += f"Σφάλμα κατά την μετατροπή της ημερομηνίας αλλαγής ονόματος χρήστη: {e}\n"
    if user_info.get('nickNameModifyTime'):
        try:
            nickname_modify_time = datetime.fromtimestamp(user_info['nickNameModifyTime'])
            formatted_nickname_modify_time = format_datetime(nickname_modify_time, "EEEE, d MMMM y - HH:mm:ss", locale='el')
            info_text += f"Ημερομηνία Αλλαγής Ψευδωνύμου: {formatted_nickname_modify_time}\n"
        except Exception as e:
            info_text += f"Σφάλμα κατά την μετατροπή της ημερομηνίας αλλαγής ψευδωνύμου: {e}\n"
    info_text += f"Επαληθευμένος: {'Ναι' if user_info.get('verified', False) else 'Όχι'}\n"
    if user_info.get('bioLink', {}).get('link'):
        info_text += f"Σύνδεσμος Bio: {user_info['bioLink']['link']}\n"
    if user_info.get('region'):
        info_text += f"Περιοχή: {user_info.get('region')}\n"
    if user_info.get('language'):
        info_text += f"Γλώσσα: {user_info.get('language')}\n"
    if user_info.get('category'):
        info_text += f"Κατηγορία: {user_info.get('category')}\n"
    if stats_info.get('followerCount', 0):
        info_text += f"Ακόλουθοι: {stats_info.get('followerCount')}\n"
    if stats_info.get('followingCount', 0):
        info_text += f"Ακολουθεί: {stats_info.get('followingCount')}\n"
    if stats_info.get('friendCount', 0):
        info_text += f"Φίλοι: {stats_info.get('friendCount')}\n"
    if stats_info.get('heart', 0):
        info_text += f"Καρδιές: {stats_info.get('heart')}\n"
    if stats_info.get('videoCount', 0):
        info_text += f"Βίντεο: {stats_info.get('videoCount')}\n"
    comments_file = f"G:\\Script\\check_tiktok_live\\Comments\\{username}_comments_analysis.txt"
    if os.path.exists(comments_file):
        try:
            total, positive, negative, neutral, positive_stars, negative_stars, neutral_stars, total_stars = count_comments(comments_file)
            info_text += f"Σχόλια: Συνολικά: {total}, Θετικά: {positive} (Αστέρια: {positive_stars}), Αρνητικά: {negative} (Αστέρια: {negative_stars}), Ουδέτερα: {neutral} (Αστέρια: {neutral_stars}), Συνολικά Αστέρια: {total_stars}\n"
        except ValueError as e:
            info_text += f"Σφάλμα κατά την ανάλυση των σχολίων: {e}\n"
    else:
        info_text += "Δεν βρέθηκαν σχόλια.\n"
    live_history = get_live_history(username)
    last_live_info = live_history[0] if live_history else "Δεν βρέθηκε ιστορικό live."
    info_text += f"Τελευταίο Live: {last_live_info}\n"
    live_history = get_live_history(username)
    if live_history:
        durations, total_duration = get_live_durations(live_history, live_users, username)
        if durations and total_duration > 0:
            daily_lives = sum(1 for d in durations if d <= 24 * 60)
            weekly_lives = sum(1 for d in durations if d <= 7 * 24 * 60)
            monthly_lives = sum(1 for d in durations if d <= 30 * 24 * 60)
            yearly_lives = sum(1 for d in durations if d <= 365 * 24 * 60)
            average_duration = total_duration / len(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            formatted_total_duration = format_duration(total_duration)
            formatted_average_duration = format_duration(average_duration)
            formatted_max_duration = format_duration(max_duration)

            info_text += (f"Συνολική Διάρκεια Live: {formatted_total_duration}, "
                          f"Μέσος Όρος Live: {formatted_average_duration}, "
                          f"Μέγιστη Διάρκεια Live: {formatted_max_duration}\n")
            info_text += (f"Live ανά Ημέρα: {daily_lives}, "
                          f"Live ανά Εβδομάδα: {weekly_lives}, "
                          f"Live ανά Μήνα: {monthly_lives}, "
                          f"Live ανά Έτος: {yearly_lives}\n")
        else:
            info_text += "Δεν υπάρχουν διαθέσιμες καταγεγραμμένες διάρκειες live.\n"
    else:
        info_text += "Δεν βρέθηκε ιστορικό live.\n"

    current_popup = tk.Toplevel(root)
    current_popup.title(f"Πληροφορίες για {username}")
    current_popup.geometry(settings['profile_settings']['default_profile_window_size'] + "+" + settings['profile_settings']['default_profile_window_position'])
    current_popup.configure(bg='black')
    error_label = tk.Label(current_popup, bg='black', fg=settings['profile_settings']['error_label_color'])
    error_label.grid(row=7, column=0, pady=1)

    # Φόρτωση μόνο της θέσης του παραθύρου, αν υπάρχει αποθηκευμένη
    position = load_window_position(current_popup, f"profile_{username}")
    if position is None:
        current_popup.geometry(settings['profile_settings']['default_profile_window_size'] + "+" + settings['profile_settings']['default_profile_window_position'])
    
    label = tk.Label(current_popup, text=info_text, font=tuple(settings['profile_settings']['label_font']), fg='white', bg='black', justify=tk.LEFT)
    label.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
    
    # Προσθήκη κουμπιού για προβολή ιστορικού live σε νέο παράθυρο
    def show_live_history():
        live_history_window = tk.Toplevel(current_popup)
        live_history_window.title(f"Ιστορικό Live για {username}")
        live_history_window.geometry(f"{settings['profile_settings']['live_history_window_size']}+{settings['profile_settings']['live_history_window_position']}")
        live_history_window.configure(bg=settings['profile_settings']['text_widget_bg'])

        # Προσθήκη γραμμής κύλισης
        scrollbar = tk.Scrollbar(live_history_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(live_history_window, 
                              font=tuple(settings['profile_settings']['text_widget_font']), 
                              fg=settings['profile_settings']['text_widget_fg'], 
                              bg=settings['profile_settings']['text_widget_bg'], 
                              wrap=tk.WORD, 
                              yscrollcommand=scrollbar.set)
        text_widget.pack(expand=True, fill=tk.BOTH)
    
        for entry in live_history:
            text_widget.insert(tk.END, entry + "\n")
    
        scrollbar.config(command=text_widget.yview)

    # Προσθήκη κουμπιού για προβολή σχολίων σε νέο παράθυρο
    def show_comments():
        comments_window = tk.Toplevel(current_popup)
        comments_window.title(f"Σχόλια για {username}")
        comments_window.geometry(f"{settings['profile_settings']['comments_window_size']}+{settings['profile_settings']['comments_window_position']}")
        comments_window.configure(bg=settings['profile_settings']['text_widget_bg'])

        # Προσθήκη γραμμής κύλισης
        scrollbar = tk.Scrollbar(comments_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(comments_window, 
                              font=tuple(settings['profile_settings']['text_widget_font']), 
                              fg=settings['profile_settings']['text_widget_fg'], 
                              bg=settings['profile_settings']['text_widget_bg'], 
                              wrap=tk.WORD, 
                              yscrollcommand=scrollbar.set)
        text_widget.pack(expand=True, fill=tk.BOTH)

        # Ανάγνωση σχολίων από το αρχείο
        log_filename = f"G:\\Script\\check_tiktok_live\\Comments\\{username}_comments_log.txt"
        try:
            with open(log_filename, "r", encoding="utf-8") as file:
                comments = file.readlines()
                for comment in comments:
                    text_widget.insert(tk.END, comment + "\n")
        except FileNotFoundError:
            text_widget.insert(tk.END, "Δεν βρέθηκαν σχόλια.\n")
    
        scrollbar.config(command=text_widget.yview)

    current_popup.protocol("WM_DELETE_WINDOW", lambda: [save_window_position(current_popup, f"profile_{username}"), current_popup.destroy()])

    avatar_urls = {
        "Μεγάλο": user_info.get('avatarLarger', ''),
        "Μεσαίο": user_info.get('avatarMedium', ''),
        "Μικρό": user_info.get('avatarThumb', '')
    }

    def display_image(size):
        avatar_url = avatar_urls.get(size, '')
        default_icon_url = "https://www.tiktok.com/favicon.ico"
    
        if avatar_url:
            try:
                response = requests.get(avatar_url)
                response.raise_for_status()
                image_data = response.content
                image = Image.open(io.BytesIO(image_data))

                # Προσαρμογή μεγέθους εικόνας ώστε να χωράει στο παράθυρο προφίλ
                max_width, max_height = 400, 400
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                image_label.config(image=photo)
                image_label.image = photo
            except requests.RequestException as e:
                error_label_color = settings['profile_settings']['error_label_color']
                error_label.config(text="Σφάλμα κατά τη λήψη της εικόνας.", fg=error_label_color)
                avatar_url = default_icon_url  # Αναπροσαρμογή του avatar_url στο προεπιλεγμένο εικονίδιο
                try:
                    response = requests.get(avatar_url)
                    response.raise_for_status()
                    image_data = response.content
                    default_image = Image.open(io.BytesIO(image_data))
                    photo = ImageTk.PhotoImage(default_image)
                    image_label.config(image=photo)
                    image_label.image = photo
                except requests.RequestException as e:
                    print("Σφάλμα κατά τη λήψη του προεπιλεγμένου εικονιδίου:", e)
        else:
            avatar_url = default_icon_url
        try:
            response = requests.get(avatar_url)
            response.raise_for_status()
            image_data = response.content
            default_image = Image.open(io.BytesIO(image_data))
            photo = ImageTk.PhotoImage(default_image)
            image_label.config(image=photo)
            image_label.image = photo
        except requests.RequestException as e:
            print("Σφάλμα κατά τη λήψη του προεπιλεγμένου εικονιδίου:", e)

    def open_full_size_image(image_url):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            photo = ImageTk.PhotoImage(image)

            full_size_popup = tk.Toplevel(root)
            full_size_popup.title("Πλήρες Μέγεθος Εικόνας")
            full_size_popup.geometry(f"{image.width}x{image.height}")
            full_size_label = tk.Label(full_size_popup, image=photo)
            full_size_label.image = photo
            full_size_label.pack()
        except requests.RequestException as e:
            print("Σφάλμα κατά τη λήψη της εικόνας:", e)

    image_label = tk.Label(current_popup, bg='black')
    image_label.grid(row=1, column=0, rowspan=6, pady=1)

    # Χρήση των ρυθμίσεων για τα μεγέθη avatar
    size_options = ["Μεγάλο", "Μεσαίο", "Μικρό"]
    size_var = tk.StringVar(value="Μεγάλο")
    size_menu = ttk.OptionMenu(current_popup, size_var, "Μεγάλο", *size_options, command=display_image)
    size_menu.grid(row=1, column=1, pady=1)

    display_image(size_options[3])  # Προβολή της μεγάλης εικόνας κατά την αρχική φόρτωση

    # Δημιουργία πλαισίου για τα κουμπιά
    button_frame = tk.Frame(current_popup, bg='black')
    button_frame.grid(row=2, column=1, rowspan=5, pady=5)

    # Προσθήκη κουμπιών με χρήση grid μέσα στο πλαίσιο
    button_font = tuple(settings['profile_settings']['button_font'])

    full_size_button_config = settings['profile_settings']['button_colors']['full_size_button']
    full_size_button = tk.Button(button_frame, text="Πλήρες Μεγέθος", command=lambda: open_full_size_image(avatar_urls.get(size_var.get(), '')), font=button_font, **full_size_button_config)
    full_size_button.grid(row=0, column=0, padx=2, pady=2)

    save_button_config = settings['profile_settings']['button_colors']['save_button']
    save_button = tk.Button(button_frame, text="Αποθήκευση Θέσης", command=lambda: save_window_position(current_popup, f"profile_{username}"), font=button_font, **save_button_config)
    save_button.grid(row=0, column=1, padx=2, pady=2)
    
    toggle_button_config = settings['profile_settings']['button_colors']['toggle_button']
    toggle_button = tk.Button(button_frame, text="Ιστορικό των Live", command=show_live_history, font=button_font, **toggle_button_config)
    toggle_button.grid(row=3, column=2, padx=2, pady=2)
    
    comments_button_config = settings['profile_settings']['button_colors']['comments_button']
    comments_button = tk.Button(button_frame, text="Προβολή Σχολίων", command=show_comments, font=button_font, **comments_button_config)
    comments_button.grid(row=0, column=2, padx=2, pady=2)

    # Προσθήκη κουμπιών εξαγωγής με χρήση grid μέσα στο πλαίσιο
    def export_info(format):
        if format == 'csv':
            export_profile_info_to_csv(username)
        elif format == 'json':
            export_profile_info_to_json(username)
        elif format == 'txt':
            export_profile_info_to_txt(username)
        elif format == 'pdf':
            export_profile_info_to_pdf(username)
        elif format == 'jpg':
            export_profile_image_to_jpg(username, avatar_urls.get(size_var.get(), ''))

    export_button_csv_config = settings['profile_settings']['button_colors']['export_button_csv']
    export_button_csv = tk.Button(button_frame, text="Εξαγωγή σε CSV", command=lambda: export_info('csv'), font=button_font, **export_button_csv_config)
    export_button_csv.grid(row=3, column=0, padx=2, pady=2)
    
    export_button_json_config = settings['profile_settings']['button_colors']['export_button_json']
    export_button_json = tk.Button(button_frame, text="Εξαγωγή σε JSON", command=lambda: export_info('json'), font=button_font, **export_button_json_config)
    export_button_json.grid(row=4, column=0, padx=2, pady=2)

    export_button_txt_config = settings['profile_settings']['button_colors']['export_button_txt']
    export_button_txt = tk.Button(button_frame, text="Εξαγωγή σε TXT", command=lambda: export_info('txt'), font=button_font, **export_button_txt_config)
    export_button_txt.grid(row=3, column=1, padx=2, pady=2)

    export_button_jpg_config = settings['profile_settings']['button_colors']['export_button_jpg']
    export_button_jpg = tk.Button(button_frame, text="Εξαγωγή σε JPG", command=lambda: export_info('jpg'), font=button_font, **export_button_jpg_config)
    export_button_jpg.grid(row=4, column=1, padx=2, pady=2)
    
    close_button_config = settings['profile_settings']['button_colors']['close_button']
    close_button = tk.Button(button_frame, text="Κλείσιμο Παραθύρου", command=current_popup.destroy, font=("Helvetica", 17), bg='red', fg='white')
    close_button.grid(row=5, column=0, padx=2, pady=2)
    
def save_window_position(window, key_prefix):
    try:
        if window.winfo_exists():  # Ελέγχει αν το παράθυρο υπάρχει
            if 'window_positions' not in settings:
                settings['window_positions'] = {}
            settings['window_positions'][key_prefix] = {
                "x": window.winfo_x(),
                "y": window.winfo_y(),
                "width": window.winfo_width(),
                "height": window.winfo_height()
            }
            save_settings()
            print(f"Αποθηκεύτηκε η θέση και το μέγεθος του παραθύρου με κλειδί {key_prefix}.")
    except Exception as e:
        print(f"Σφάλμα κατά την αποθήκευση της θέσης και του μεγέθους του παραθύρου: {e}")

def load_window_position(window, key_prefix):
    try:
        if 'window_positions' in settings and key_prefix in settings['window_positions']:
            position = settings['window_positions'][key_prefix]
            window.geometry(f"{position['width']}x{position['height']}+{position['x']}+{position['y']}")
            print(f"Φορτώθηκε η θέση και το μέγεθος του παραθύρου με κλειδί {key_prefix}.")
            return position
        else:
            print("Δεν υπάρχει αποθηκευμένη θέση.")
            return None
    except Exception as e:
        print(f"Σφάλμα κατά τη φόρτωση της θέσης και του μεγέθους του παραθύρου: {e}.")
        return None

def call_insert_m3u_script():
    os.system(f"python {settings['other_settings'].get('insert_m3u_script', 'insert_tiktok_m3u_in_playlist.py')}")

def check_live_one_user():
    subprocess.Popen(["python", settings['other_settings'].get('check_live_one_user_with_loop', 'check_live_one_user_with_loop.py')], creationflags=subprocess.CREATE_NEW_CONSOLE)

def call_check_twitch_live():
    subprocess.Popen(["python", settings['other_settings'].get('check_twitch_live', 'check_twitch_live.py')], creationflags=subprocess.CREATE_NEW_CONSOLE)
    
def call_check_trovo_live():
    subprocess.Popen(["python", settings['other_settings'].get('check_trovo_live', 'check_trovo_live.py')], creationflags=subprocess.CREATE_NEW_CONSOLE)

def call_gift():
    subprocess.Popen(["python", settings['other_settings'].get('gifts_script', 'gifts.py')], creationflags=subprocess.CREATE_NEW_CONSOLE)

def call_check_proxy_script():
    subprocess.Popen(["python", settings['other_settings'].get('check_proxy_script', 'check_proxy_active.py')], creationflags=subprocess.CREATE_NEW_CONSOLE)

def call_scrape_profile_script():
    subprocess.Popen(["python", settings['other_settings'].get('scrape_profile_script', 'scrape_profile_tiktok_checkbox.py')], creationflags=subprocess.CREATE_NEW_CONSOLE)

def start_comment_script():
    subprocess.Popen(["python", settings['other_settings'].get('comment_script', 'check_tiktok_live_comment.py')], creationflags=subprocess.CREATE_NEW_CONSOLE)

def call_comments_and_gift():
    subprocess.Popen(["python", settings['other_settings'].get('comments_and_gifts_script', 'comments_and_gifts_like_follow.py')], creationflags=subprocess.CREATE_NEW_CONSOLE)

def create_gui():
    global settings, root, live_users_listbox, unique_users_label, active_live_count, sound_checkbox, loop_checkbox, countdown_label, minutes_var, menubar, settings_menu, about_menu, help_menu, interval_frame, button_frame, option_menu, label, minutes_label, color_menu, alert_sound, always_on_top, label_interval_search, label_minutes, users_button, m3u_live_count_label

    root = tk.Tk()
    root.title("Χρήστες σε live")
    root.geometry("265x560+1645+420")
    root.configure(bg=settings.get('general_settings', {}).get('background_color', 'black'))

    active_live_count = 0
    alert_sound = settings.get("general_settings", {}).get("alert_sound", "default_sound.wav")
    always_on_top = settings.get("general_settings", {}).get("always_on_top", True)
    root.attributes("-topmost", always_on_top)

    menubar = tk.Menu(root, font=("Helvetica", 14))
    settings_menu = tk.Menu(menubar, tearoff=0, bg='black', fg='white', font=("Helvetica", 14))

    settings_menu.add_command(label="Επιλογή Ήχου Ειδοποίησης", command=lambda: select_sound_file())
    settings_menu.add_command(label="Πάντα στην κορυφή", command=lambda: toggle_always_on_top())
    settings_menu.add_command(label="Scrape Προφιλ", command=call_scrape_profile_script)
    settings_menu.add_command(label="Έλεγχος ΤικΤοκ Live Plus", command=check_live_one_user)
    settings_menu.add_command(label="Έλεγχος Twitch Live", command=call_check_twitch_live)
    settings_menu.add_command(label="Έλεγχος Trovo Live", command=call_check_trovo_live)
    settings_menu.add_command(label="Έλεγχος Proxy", command=call_check_proxy_script)
    settings_menu.add_command(label="Δώρα Χρηστών", command=call_gift)
    settings_menu.add_command(label="Παράθυρο Σχολίων", command=start_comment_script)
    settings_menu.add_command(label="Σχόλια και Δώρα Χρηστών", command=call_comments_and_gift)
    settings_menu.add_command(label="Εισαγωγή lives στο BlueddoTiVi", command=call_insert_m3u_script)

    color_menu = tk.Menu(settings_menu, tearoff=0, bg='black', fg='white', font=("Helvetica", 14))
    colors = [("Μαύρο", "black"), ("Άσπρο", "white"), ("Μπλε", "blue"), ("Κόκκινο", "red"),
              ("Πράσινο", "green"), ("Μωβ", "purple"), ("Πορτοκαλί", "orange"), ("Κίτρινο", "yellow"),
              ("Ροζ", "pink"), ("Γκρι", "gray")]

    for name, color in colors:
        color_menu.add_command(label=name, command=lambda color=color: change_background_color(color))
        
    settings_menu.add_cascade(label="Αλλαγή Χρώματος Φόντου", menu=color_menu)
    menubar.add_cascade(label="Ρυθμίσεις", menu=settings_menu)
    root.config(menu=menubar)

    label = tk.Label(root, text="Έλεγχος για live...", font=("Verdana", 17, "bold"), fg='white', bg='black')
    label.pack(pady=3, fill=tk.X, expand=True)
    listbox_frame = tk.Frame(root, bg='black')
    listbox_frame.pack(pady=5, fill=tk.BOTH, expand=True)
    live_users_listbox = tk.Listbox(listbox_frame, font=("Verdana", 14), fg='white', bg='black')
    live_users_listbox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    h_scrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    live_users_listbox.config(xscrollcommand=h_scrollbar.set)
    h_scrollbar.config(command=live_users_listbox.xview)

    unique_users_label = tk.Label(root, text=f"Χρήστες: {len(load_users())} | Προφίλ: {len(profile_data)}", font=("Helvetica", 14), fg='white', bg='black')
    unique_users_label.pack(pady=1, fill=tk.X, expand=True)

    interval_frame = tk.Frame(root, bg='black')
    interval_frame.pack(pady=5, fill=tk.X, expand=True)

    minutes_var = tk.StringVar(value=settings.get("general_settings", {}).get("search_interval", "1"))
    label_interval_search = tk.Label(interval_frame, text="Αναζήτηση σε: ", font=("Helvetica", 12), fg='white', bg='black')
    label_interval_search.pack(side=tk.LEFT)

    option_menu = tk.OptionMenu(interval_frame, minutes_var, "1", "2", "5", "10", "15", "30", command=update_interval)
    option_menu.config(font=("Helvetica", 14), fg='white', bg='black')
    option_menu['menu'].config(font=("Helvetica", 14), bg='black', fg='white')
    for item in option_menu['menu'].winfo_children():
        item.config(bg='black', fg='white', font=("Helvetica", 24))  # Ενημέρωση του φόντου και της γραμματοσειράς

    option_menu.pack(side=tk.LEFT)

    label_minutes = tk.Label(interval_frame, text="λεπτά", font=("Helvetica", 12), fg='white', bg='black')
    label_minutes.pack(side=tk.LEFT)

    countdown_label = tk.Label(root, text="Επόμενη αναζήτηση σε: 00:00", font=("Helvetica", 12), fg='white', bg='black')
    countdown_label.pack(pady=1, fill=tk.X, expand=True)

    loop_var = tk.BooleanVar(value=settings.get("general_settings", {}).get("loop_enabled", True))
    loop_checkbox = tk.Checkbutton(root, text="Απενεργοποίηση έλεγχου", variable=loop_var, command=toggle_loop, font=("Helvetica", 12), fg='white', bg='black', selectcolor='black')
    loop_checkbox.pack(pady=1, fill=tk.X, expand=True)

    sound_enabled = settings.get("general_settings", {}).get('sound_enabled', True)
    sound_checkbox = tk.Checkbutton(root, text="Ενεργ. Ηχητικής Ειδοποίησης", command=toggle_sound, font=("Helvetica", 12), fg='white', bg='black', selectcolor='black')
    sound_checkbox.select() if sound_enabled else sound_checkbox.deselect()
    sound_checkbox.pack(pady=1, fill=tk.X, expand=True)

    button_frame = tk.Frame(root, bg='black')
    button_frame.pack(pady=5, fill=tk.X, expand=True)
    start_button = tk.Button(button_frame, text="Ανοιγμα Client", command=call_comments_and_gift, font=("Helvetica", 12), fg='white', bg='blue')
    start_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    users_button = tk.Button(button_frame, text="Προφιλ", command=open_user_menu, font=("Helvetica", 12), fg='white', bg='green')
    users_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    clear_icon = Image.open("clear_icon.png")
    clear_icon = clear_icon.resize((20, 20), Image.Resampling.LANCZOS)
    clear_photo = ImageTk.PhotoImage(clear_icon)
    clear_button = tk.Button(button_frame, text="", command=clear_listbox, font=("Helvetica", 12), fg='white', bg='red', image=clear_photo, compound=tk.LEFT)
    clear_button.image = clear_photo
    clear_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    # Αποθήκευση των τρέχουσων ρυθμίσεων
    save_window_position(root, "main_window")
    settings['general_settings']['background_color'] = root['bg']
    settings['general_settings']['always_on_top'] = root.attributes("-topmost")
    settings['general_settings']['search_interval'] = minutes_var.get()
    settings['general_settings']['loop_enabled'] = loop_enabled
    settings['general_settings']['sound_enabled'] = sound_enabled
    save_settings()
    
    # Όταν η εφαρμογή κλείνει, αποθηκεύουμε τις ρυθμίσεις
    root.protocol("WM_DELETE_WINDOW", lambda: [save_window_position(root, "main_window"), save_settings(), root.destroy()])

    search_interval = 1
    url_cache = {} # Προσωρινή μνήμη για τις συντομευμένες διευθύνσεις URL
    
def change_background_color(color):
    color_settings = settings['general_settings']['colors'].get(color, settings['general_settings']['colors']['unknown'])
    fg_color = color_settings['fg_color']
    font = tuple(color_settings['font'])
    listbox_font = tuple(color_settings['listbox_font'])
    menu_font = tuple(color_settings['menu_font'])
    color_name = color
    font_name = fg_color
    
    elements = [root, live_users_listbox, unique_users_label, countdown_label, button_frame, interval_frame, loop_checkbox, sound_checkbox, option_menu, color_menu, settings_menu, minutes_var, users_button]
    for element in elements:
        if hasattr(element, 'config'):
            try:
                element.config(bg=color, fg=fg_color, font=font)
                print(f"Αλλαγή {element} σε φόντο {color_name} και χρώμα γραμματοσειράς {font_name}")
            except tk.TclError:
                element.config(bg=color)
                print(f"Αλλαγή {element} σε φόντο {color_name}")

    live_users_listbox.config(bg=color, fg=fg_color, font=listbox_font)
    print(f"Αλλαγή live_users_listbox σε φόντο {color_name} και χρώμα γραμματοσειράς {font_name}")

    option_menu.config(bg=color, highlightbackground=color, highlightcolor=color, activebackground=color, activeforeground=fg_color)
    option_menu['menu'].config(bg=color, font=menu_font, fg='black')
    for item in option_menu['menu'].winfo_children():
        item.config(bg=color, fg='black', font=menu_font)
        print(f"Αλλαγή στοιχείου μενού σε φόντο {color_name} και χρώμα γραμματοσειράς μαύρο")

    loop_checkbox.config(selectcolor=color)
    sound_checkbox.config(selectcolor=color)

    label_interval_search.config(fg=fg_color, bg=color, font=font)
    print(f"Αλλαγή label_interval_search σε φόντο {color_name} και χρώμα γραμματοσειράς {font_name}")

    label_minutes.config(fg=fg_color, bg=color, font=font)
    print(f"Αλλαγή label_minutes σε φόντο {color_name} και χρώμα γραμματοσειράς {font_name}")

    label.config(bg=color, fg=fg_color, font=("Verdana", 17))
    print(f"Αλλαγή label σε φόντο {color_name} και χρώμα γραμματοσειράς {font_name}")

    users_button.config(bg=color, fg=fg_color)
    print(f"Αλλαγή κουμπιού χρηστών σε φόντο {color_name} και χρώμα γραμματοσειράς {font_name}")

    try:
        menubar.config(bg=color)
        settings_menu.config(bg=color)
        print(f"Αλλαγή μπάρας μενού και ρυθμίσεων σε φόντο {color_name}")
    except tk.TclError:
        pass

    settings['general_settings']['background_color'] = color
    save_settings()

def is_valid_url(url):
    return validators.url(url)

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
    
def clear_listbox():
    live_users_listbox.delete(0, tk.END)

def check_user(user):
    result = subprocess.run(
        ["streamlink", "--stream-url" "https://www.tiktok.com/@{}".format(user), "best"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    
    if output.startswith("https://pull-f5-tt0"):
        start_time = datetime.now().strftime("%H:%M:%S")
        if user not in live_stats:
            live_stats
        if sound_enabled and user not in notified_users:
            winsound.PlaySound(alert_sound, winsound.SND_FILENAME)
            notified_users.add(user)
        return user, output, start_time
    return user, None, None

def check_live_users():
    global running, active_live_count
    running = True
    live_users = {}
    previous_live_users = {}  # Κρατάει τους χρήστες που ήταν σε live στον προηγούμενο έλεγχο και την ώρα που ξεκίνησαν
    users = load_users()  # Φόρτωση των χρηστών από το αρχείο
    # Ενημέρωση του loop για να ελέγχει την κατάσταση της αντίστροφης μέτρησης και να εμφανίζει το κατάλληλο μήνυμα
    while running:
        if not loop_enabled:
            countdown_label.config(text="Ο έλεγχος απενεργοποιήθηκε")
            print("Ο έλεγχος απενεργοποιήθηκε. Περιμένω για την επανενεργοποίηση...")
            while not loop_enabled:
                time.sleep(1)  # Αναμονή μέχρι να ενεργοποιηθεί ο βρόχος ξανά
        elif not countdown_active:
            countdown_label.config(text="Η Αναζήτηση ειναι σε εξέλιξη...")

        current_live_users = {}
        print("Ξεκινάει ο έλεγχος των χρηστών για αναζήτηση live...")

        with alive_bar(len(users), title='Έλεγχος χρηστών', bar='smooth', spinner='waves') as bar:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(check_user, user): user for user in users}
                for future in as_completed(futures):
                    user, output, start_time = future.result()
                    if output:
                        current_live_users[user] = (output, start_time)
                        status = colored("είναι σε live", "yellow", "on_blue", attrs=["bold", "blink"])
                        if user not in previous_live_users:
                            previous_live_users[user] = start_time
                            live_users_listbox.insert(tk.END, f" {user} --> {start_time} ")
                            unique_users.add(user)
                            active_live_count = len(current_live_users)
                            unique_users_label.config(text=f"Μοναδικοί: {len(unique_users)} Live: {active_live_count} m3u: {len(live_users)}")
                            with open("live_history_tiktok.log", "a", encoding="utf-8") as log_file:
                                formatted_date = format_datetime(datetime.now(), "EEEE, d MMMM y - HH:mm:ss", locale='el')
                                log_file.write(f"{formatted_date} - {user} - βρέθηκε live\n")
                            live_users[user] = (output, start_time)
                            update_m3u_file(live_users)
                            last_live_links[user] = output
                        else:
                            live_users[user] = (output, previous_live_users[user])
                    else:
                        if user in previous_live_users:
                            end_time = datetime.now().strftime("%H:%M:%S")
                            with open("live_history_tiktok.log", "a", encoding="utf-8") as log_file:
                                formatted_date = format_datetime(datetime.now(), "EEEE, d MMMM y - HH:mm:ss", locale='el')
                                log_file.write(f"{formatted_date} - {user} - σταμάτησε το live\n")
                            del previous_live_users[user]
                        status = "δεν είναι σε live"
                    print(f"Έλεγχος χρήστη: {user} - {status}")
                    bar()

        live_users = current_live_users
        print("Ο έλεγχος ολοκληρώθηκε. Αναμονή για τον επόμενο κύκλο...")
        subprocess.run(["python", "insert_tiktok_m3u_in_playlist.py"])
        start_countdown(loop_interval)

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
                        short_avatar_thumb = avatar_thumb  # Χρησιμοποιούμε το αρχικό avatar_thumb
                    
                    if short_avatar_thumb is None:
                        short_avatar_thumb = avatar_thumb
                    
                    write_m3u_entry(m3u_file, short_avatar_thumb, user, start_time, output)
                    user_count += 1
                logging.info(f"Τα δεδομένα προφίλ του χρήστη {user} έχουν φορτωθεί. Συνολικά: {len(profile_data)}.")
                logging.info(f"Το αρχείο M3U ενημερώθηκε επιτυχώς με τον χρήστη {user}. Συνολικά: {user_count} live.")
            else:
                write_default_stream(m3u_file, default_stream_url)
                logging.info("Το αρχείο M3U ενημερώθηκε επιτυχώς.")
        
        # Ενημέρωση της ετικέτας στο Tkinter GUI
        unique_users_label.config(text=f"Μοναδικοί: {len(unique_users)} Live: {active_live_count} m3u: {len(live_users)}")
    
    except Exception as e:
        logging.error(f"Σφάλμα κατά την ενημέρωση του αρχείου m3u: {e}")
        with open("tiktok_live.m3u", "w", encoding="utf-8") as m3u_file:
            write_m3u_header(m3u_file)
            write_default_stream(m3u_file, default_stream_url)
        logging.info("Προστέθηκε το προεπιλεγμένο stream λόγω σφάλματος.")

def write_m3u_header(m3u_file):
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

def write_m3u_entry(m3u_file, short_avatar_thumb, user, start_time, output):
    group_title = settings['general_settings']['group_title']
    tvg_id = settings['general_settings']['tvg_id']
    m3u_file.write(f"#EXTINF:-1 group-title=\"{group_title}\" tvg-logo=\"{short_avatar_thumb}\" tvg-id=\"{tvg_id}\" $ExtFilter=\"Tikitok live\",{user}\n")
    m3u_file.write(f"{output}\n")

def write_default_stream(m3u_file, default_stream_url):
    group_title = settings['general_settings']['group_title']
    tvg_id = settings['general_settings']['tvg_id']
    m3u_file.write(f"#EXTINF:-1 group-title=\"{group_title}\" tvg-logo=\"https://www.tiktok.com/favicon.ico\" tvg-id=\"{tvg_id}\" $ExtFilter=\"Tikitok live\",Default Stream\n")
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
        response.raise_for_status()  # Βεβαιωνετε ότι το αίτημα ήταν επιτυχές
        return True
    except requests.RequestException:
        return False

def update_interval(*args):
    global loop_interval
    minutes = int(minutes_var.get())  # Λαμβάνει την τιμή των λεπτών από τη μεταβλητή minutes_var.
    loop_interval = minutes * 60  # Μετατρέπει τα λεπτά σε δευτερόλεπτα και τα αποθηκεύει στο loop_interval.
    settings['general_settings']['search_interval'] = minutes_var.get()
    save_settings()
    print(f"Το διάστημα αναζήτησης ορίστηκε σε {minutes} λεπτά.")
        
def start_countdown(seconds):
    global countdown_active
    countdown_active = True
    end_time = datetime.now() + timedelta(seconds=seconds)
    while datetime.now() < end_time:
        remaining_time = end_time - datetime.now()
        minutes, seconds = divmod(remaining_time.seconds, 60)
        countdown_label.config(text=f"Επόμενη αναζήτηση σε: {minutes:02}:{seconds:02}")
        print(f"Χρόνος μέχρι τον επόμενο έλεγχο: {minutes:02}:{seconds:02} - {remaining_time.seconds} δευτερόλεπτα", end="\r")
        time.sleep(1)
    countdown_active = False
    countdown_label.config(text="Η αντίστροφη μέτρηση ολοκληρώθηκε.")
        
# Συνάρτηση για την ενεργοποίηση/απενεργοποίηση του βρόχου
def toggle_loop():
    global loop_enabled
    loop_enabled = not loop_enabled
    settings['general_settings']['loop_enabled'] = loop_enabled
    save_settings()
    print(f"Ο Ελεγχος ειναι {'ενεργοποιημένος' if loop_enabled else 'απενεργοποιημένος'}")

# Συνάρτηση για την ενεργοποίηση/απενεργοποίηση του ήχου
def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    settings['general_settings']['sound_enabled'] = sound_enabled
    save_settings()
    print(f"Η ηχητική ειδοποίηση είναι {'ενεργοποιημένη' if sound_enabled else 'απενεργοποιημένη'}")

# Επιλογή ήχου ειδοποίησης
def select_sound_file():
    global alert_sound
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        alert_sound = file_path
        settings['general_settings']['alert_sound'] = alert_sound
        save_settings()
        print(f"Επιλέχθηκε ήχος ειδοποίησης: {alert_sound}")

# Ελαχιστοποίηση κονσόλας
def minimize_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)

# Συνάρτηση για το κλείσιμο του παραθύρου
def on_closing():
    global running
    running = False
    load_settings()  # Επαναφορά των αποθηκευμένων ρυθμίσεων
    root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
def export_profile_info_to_csv(username):
    user_data = next((item for item in profile_data if item['user']['uniqueId'] == username), {})
    user_info = user_data.get("user", {})
    stats_info = user_data.get("stats", {})
    with open(f"{username}_profile_info.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Πεδίο", "Τιμή"])
        
        # Αν δεν υπάρχει πληροφορία, να γράφει "Μη διαθέσιμο"
        writer.writerow(["Όνομα χρήστη", user_info.get('uniqueId', 'Μη διαθέσιμο')])
        writer.writerow(["Ψευδώνυμο", user_info.get('nickname', 'Μη διαθέσιμο')])
        writer.writerow(["Περιγραφή", user_info.get('signature', 'Μη διαθέσιμο')])
        
        create_time = user_info.get('createTime', 'Μη διαθέσιμο')
        if create_time != 'Μη διαθέσιμο':
            create_time = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow(["Ημερομηνία Δημιουργίας", create_time])
        
        unique_id_modify_time = user_info.get('uniqueIdModifyTime', 'Μη διαθέσιμο')
        if unique_id_modify_time != 'Μη διαθέσιμο':
            unique_id_modify_time = datetime.fromtimestamp(unique_id_modify_time).strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow(["Ημερομηνία Αλλαγής Ονόματος Χρήστη", unique_id_modify_time])
        
        nick_name_modify_time = user_info.get('nickNameModifyTime', 'Μη διαθέσιμο')
        if nick_name_modify_time != 'Μη διαθέσιμο':
            nick_name_modify_time = datetime.fromtimestamp(nick_name_modify_time).strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow(["Ημερομηνία Αλλαγής Ψευδωνύμου", nick_name_modify_time])
        
        writer.writerow(["Επαληθευμένος", 'Ναι' if user_info.get('verified', False) else 'Όχι'])
        writer.writerow(["Σύνδεσμος Bio", user_info.get('bioLink', {}).get('link', 'Μη διαθέσιμο')])
        writer.writerow(["Περιοχή", user_info.get('region', 'Μη διαθέσιμο')])
        writer.writerow(["Γλώσσα", user_info.get('language', 'Μη διαθέσιμο')])
        writer.writerow(["Κατηγορία", user_info.get('category', 'Μη διαθέσιμο')])
        writer.writerow(["Ακόλουθοι", stats_info.get('followerCount', 'Μη διαθέσιμο')])
        writer.writerow(["Ακολουθεί", stats_info.get('followingCount', 'Μη διαθέσιμο')])
        writer.writerow(["Φίλοι", stats_info.get('friendCount', 'Μη διαθέσιμο')])
        writer.writerow(["Καρδιές", stats_info.get('heart', 'Μη διαθέσιμο')])
        writer.writerow(["Βίντεο", stats_info.get('videoCount', 'Μη διαθέσιμο')])
        
    print(f"Οι πληροφορίες του προφίλ για τον χρήστη {username} εξήχθησαν επιτυχώς στο αρχείο {username}_profile_info.csv.")

def export_profile_info_to_json(username):
    user_data = next((item for item in profile_data if item['user']['uniqueId'] == username), {})
    user_info = user_data.get("user", {})
    stats_info = user_data.get("stats", {})

    profile_info = {
        "Όνομα χρήστη": user_info.get('uniqueId', 'Μη διαθέσιμο'),
        "Ψευδώνυμο": user_info.get('nickname', 'Μη διαθέσιμο'),
        "Περιγραφή": user_info.get('signature', 'Μη διαθέσιμο'),
        "Ημερομηνία Δημιουργίας": datetime.fromtimestamp(user_info.get('createTime')).strftime('%Y-%m-%d %H:%M:%S') if user_info.get('createTime') else 'Μη διαθέσιμο',
        "Ημερομηνία Αλλαγής Ονόματος Χρήστη": datetime.fromtimestamp(user_info.get('uniqueIdModifyTime')).strftime('%Y-%m-%d %H:%M:%S') if user_info.get('uniqueIdModifyTime') else 'Μη διαθέσιμο',
        "Ημερομηνία Αλλαγής Ψευδωνύμου": datetime.fromtimestamp(user_info.get('nickNameModifyTime')).strftime('%Y-%m-%d %H:%M:%S') if user_info.get('nickNameModifyTime') else 'Μη διαθέσιμο',
        "Επαληθευμένος": 'Ναι' if user_info.get('verified', False) else 'Όχι',
        "Σύνδεσμος Bio": user_info.get('bioLink', {}).get('link', 'Μη διαθέσιμο'),
        "Περιοχή": user_info.get('region', 'Μη διαθέσιμο'),
        "Γλώσσα": user_info.get('language', 'Μη διαθέσιμο'),
        "Κατηγορία": user_info.get('category', 'Μη διαθέσιμο'),
        "Ακόλουθοι": stats_info.get('followerCount', 'Μη διαθέσιμο'),
        "Ακολουθεί": stats_info.get('followingCount', 'Μη διαθέσιμο'),
        "Φίλοι": stats_info.get('friendCount', 'Μη διαθέσιμο'),
        "Καρδιές": stats_info.get('heart', 'Μη διαθέσιμο'),
        "Βίντεο": stats_info.get('videoCount', 'Μη διαθέσιμο')
    }

    with open(f"{username}_profile_info.json", mode='w', encoding='utf-8') as file:
        json.dump(profile_info, file, ensure_ascii=False, indent=4)

    print(f"Οι πληροφορίες του προφίλ για τον χρήστη {username} εξήχθησαν επιτυχώς στο αρχείο {username}_profile_info.json.")

def export_profile_info_to_txt(username):
    user_data = next((item for item in profile_data if item['user']['uniqueId'] == username), {})
    user_info = user_data.get("user", {})
    stats_info = user_data.get("stats", {})
    profile_image_url = user_info.get('avatarLarger', '')

    try:
        create_time = datetime.fromtimestamp(user_info.get('createTime')) if user_info.get('createTime') else 'Μη διαθέσιμο'
        unique_id_modify_time = datetime.fromtimestamp(user_info.get('uniqueIdModifyTime')) if user_info.get('uniqueIdModifyTime') else 'Μη διαθέσιμο'
        nick_name_modify_time = datetime.fromtimestamp(user_info.get('nickNameModifyTime')) if user_info.get('nickNameModifyTime') else 'Μη διαθέσιμο'
    except ValueError as e:
        print(f"Σφάλμα κατά την μετατροπή ημερομηνίας: {e}")
        create_time = unique_id_modify_time = nick_name_modify_time = 'Μη διαθέσιμο'

    info_text = f"""
    Όνομα χρήστη: {user_info.get('uniqueId', 'Μη διαθέσιμο')}
    Ψευδώνυμο: {user_info.get('nickname', 'Μη διαθέσιμο')}
    Περιγραφή: {user_info.get('signature', 'Μη διαθέσιμο')}
    Ημερομηνία Δημιουργίας: {create_time}
    Ημερομηνία Αλλαγής Ονόματος Χρήστη: {unique_id_modify_time}
    Ημερομηνία Αλλαγής Ψευδωνύμου: {nick_name_modify_time}
    Επαληθευμένος: {'Ναι' if user_info.get('verified', False) else 'Όχι'}
    Σύνδεσμος Bio: {user_info.get('bioLink', {}).get('link', 'Μη διαθέσιμο')}
    Περιοχή: {user_info.get('region', 'Μη διαθέσιμο')}
    Γλώσσα: {user_info.get('language', 'Μη διαθέσιμο')}
    Κατηγορία: {user_info.get('category', 'Μη διαθέσιμο')}
    Ακόλουθοι: {stats_info.get('followerCount', 'Μη διαθέσιμο')}
    Ακολουθεί: {stats_info.get('followingCount', 'Μη διαθέσιμο')}
    Φίλοι: {stats_info.get('friendCount', 'Μη διαθέσιμο')}
    Καρδιές: {stats_info.get('heart', 'Μη διαθέσιμο')}
    Βίντεο: {stats_info.get('videoCount', 'Μη διαθέσιμο')}
    Εικόνα προφίλ: {profile_image_url if profile_image_url else 'Μη διαθέσιμο'}
    """

    with open(f"{username}_profile_info.txt", mode='w', encoding='utf-8') as file:
        file.write(info_text.strip())
    
    print(f"Οι πληροφορίες του προφίλ για τον χρήστη {username} εξήχθησαν επιτυχώς στο αρχείο {username}_profile_info.txt.")

def export_profile_info_to_pdf(username):
    user_data = next((item for item in profile_data if item['user']['uniqueId'] == username), {})
    user_info = user_data.get("user", {})
    stats_info = user_data.get("stats", {})
    profile_image_url = user_info.get('avatarLarger', '')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Ορισμός πεδίων και αξιών
    fields = [
        ("Όνομα χρήστη", user_info.get('uniqueId', 'Μη διαθέσιμο')),
        ("Ψευδώνυμο", user_info.get('nickname', 'Μη διαθέσιμο')),
        ("Περιγραφή", user_info.get('signature', 'Μη διαθέσιμο')),
    ]

    # Μετατροπή και έλεγχος ημερομηνιών
    create_time = user_info.get('createTime', 'Μη διαθέσιμο')
    if create_time != 'Μη διαθέσιμο':
        create_time = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
    fields.append(("Ημερομηνία Δημιουργίας", create_time))

    unique_id_modify_time = user_info.get('uniqueIdModifyTime', 'Μη διαθέσιμο')
    if unique_id_modify_time != 'Μη διαθέσιμο':
        unique_id_modify_time = datetime.fromtimestamp(unique_id_modify_time).strftime('%Y-%m-%d %H:%M:%S')
    fields.append(("Ημερομηνία Αλλαγής Ονόματος Χρήστη", unique_id_modify_time))

    nick_name_modify_time = user_info.get('nickNameModifyTime', 'Μη διαθέσιμο')
    if nick_name_modify_time != 'Μη διαθέσιμο':
        nick_name_modify_time = datetime.fromtimestamp(nick_name_modify_time).strftime('%Y-%m-%d %H:%M:%S')
    fields.append(("Ημερομηνία Αλλαγής Ψευδωνύμου", nick_name_modify_time))

    fields.extend([
        ("Επαληθευμένος", 'Ναι' if user_info.get('verified', False) else 'Όχι'),
        ("Σύνδεσμος Bio", user_info.get('bioLink', {}).get('link', 'Μη διαθέσιμο')),
        ("Περιοχή", user_info.get('region', 'Μη διαθέσιμο')),
        ("Γλώσσα", user_info.get('language', 'Μη διαθέσιμο')),
        ("Κατηγορία", user_info.get('category', 'Μη διαθέσιμο')),
        ("Ακόλουθοι", stats_info.get('followerCount', 'Μη διαθέσιμο')),
        ("Ακολουθεί", stats_info.get('followingCount', 'Μη διαθέσιμο')),
        ("Φίλοι", stats_info.get('friendCount', 'Μη διαθέσιμο')),
        ("Καρδιές", stats_info.get('heart', 'Μη διαθέσιμο')),
        ("Βίντεο", stats_info.get('videoCount', 'Μη διαθέσιμο'))
    ])

    # Γράφει τις πληροφορίες στο PDF
    for field_name, value in fields:
        pdf.cell(200, 10, txt=f"{field_name}: {value}", ln=True)

    pdf.output(f"{username}_profile_info.pdf")
    print(f"Οι πληροφορίες του προφίλ για τον χρήστη {username} εξήχθησαν επιτυχώς στο αρχείο {username}_profile_info.pdf.")
    
def export_profile_image_to_jpg(username, image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = response.content
        image = Image.open(io.BytesIO(image_data))
        image_path = f"{username}_profile_image.jpg"
        image.save(image_path)
        print(f"Η εικόνα προφίλ για τον χρήστη {username} εξήχθη επιτυχώς στο αρχείο {image_path}.")
    except requests.RequestException as e:
        print("Σφάλμα κατά τη λήψη της εικόνας:", e)

if __name__ == "__main__":
    users = load_users()
    profile_data = load_profile_data()
    load_settings()
    ensure_default_settings()
    save_settings()
    unique_users = set()
    active_live_count = 0
    last_live_links = {}
    create_gui()
    thread = threading.Thread(target=check_live_users, daemon=True)
    thread.start()
    minimize_console()
    root.mainloop()
