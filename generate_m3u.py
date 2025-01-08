import subprocess
import time
from tqdm import tqdm
from termcolor import colored

# Ορισμός χρηστών TikTok
users = [
    "viktoria123_40", "sweetcookiemy", "orinimelissa", "boukitses", "mairi_mihoy_official", "mydatingexperience2", "candles.and.events", "xara_xara_xara", "poparatsaklidou", "tzwrtzina_st", "despoina_dim_", "andronikinikaki", "dwroula0", "nina_bodokia", "haroula_taotao", "karidomanna", "grintelas.com", "jimpr2grivakis",
    "mari_sweet_and_cake", "to_moviesroom", "irinious1", "seminarecipes.gr", "kaiti1959", "eirini_psychologi",
    "valentiniro", "antreastisi", "stefania_greece_4", "angelos.bam", "angelos.bam2", "viva.camper", "tasosevoia", "koemtzidoyyyy", "paraskeuopoulo",
    "kondyliam", "mariasofikiti0", "stauroulatheoxari", "ioannakoulouri180", "esperanzavanlife", "kathxhtiko", "sertsas", "ioannistserkis78",
    "tzwrtzina_st", "tzervoudakis", "lazaros.a.avramidis", "ts0plakix", "despoinabarka4", "freskia.zymi",
    "georgeporfiris", "zaxaroplastisa", "liros_zaxaroplastiki", "ibadam77", "kokkinosskoufos_skg",
    "evgenis_smusenok", "aggelikimanousaki", "sto_pi_k_fi", "tustok", "venetvlive",
    "gwgwdimou", "_______jr_______", "chris.fintr", "marwmaroy", "giannispapasifakis1",
    "krifes_alithies", "jennakivl", "mirela_kondi", "kostaspal1982",
    "vasilikigrn", "mariaaaxsl", "kwnstantina.35", "tasospapadopoulo",
    "angelstathis", "ariadni.mi", "elenimekolli17", "sindika83", "nikosgiko",
    "glorioustheoc", "basiliki_makri", "billiardgr", "user9333815415701", "konstantina.loventina",
    "mimi.m1m1ka", "harman_gr", "8meowkat8", "vasiazouganeli", "giannelis_",
    "klwntia_anna", "sofia_peridi", "journalist_presenter89", "jrramonas", "vasalos_konstantinos",
    "vaggelitsa.kol", "grandfather_handmade", "ziogasantonis", "vivianavramidou", "sophiazoezitsis",
    "filiolou", "magic_vesto", "national_star_antreoulis", "seminarecipes.gr", "passailmintinoglou",
    "petrakosthess", "leonidas_bakery", "six_senses_candles2", "georgegiannak", "piece.of.mam",
    "marymary___1", "retsamaria442", "ngradiogr", "aristea_alexandrakh", "panagiotis_milas",
    "edeirini", "anonymous_hacking_team", "pimenidisfilipos", "lenazevgara_official", "johnathan_stef",
    "orizontasgegonota", "nasia_ev", "nikos_parlantzas", "efi_gkouli96official", "vasilikibotsa",
    "besianahsj", "elena_charalampoudi", "potsepistasos", "nasia_ev", "katerinawhybe",
    "petronela_birsilaoff", "kostaspal82", "thegreekmasterchef", "kkjewelry1", "eirinikalika",
    "sertsas", "ilias_kiazoli", "user91618478129743", "poparatsaklidou", "amaliakwstaraa",
    "saliagos.nikos", "xristinadiak", "kalliopifen1",
]

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
with open("tiktok_live.m3u", "w") as m3u_file:
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

# Έλεγχος για κάθε χρήστη αν είναι live με μπάρα προόδου
for user in tqdm(users, desc="Έλεγχος χρηστών του TikTok", ncols=100):
    result = subprocess.run(
        ["streamlink", f"https://www.tiktok.com/@{user}", "worst", "--stream-url"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    
    if "error: No playable streams found on this URL" not in output:
        if output.startswith("https://"):
            status = colored("είναι σε live", "yellow", "on_blue", attrs=["bold", "blink"])
            with open("tiktok_live.m3u", "a") as m3u_file:
                m3u_file.write(f"#EXTINF:-1 group-title=\"TikTok Live\" tvg-logo=\"https://www.tiktok.com/favicon.ico\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tikitok live\",{user}\n")
                m3u_file.write(f"{output}\n")
    else:
        status = "δεν είναι σε live"
    
    tqdm.write(f"Έλεγχος χρήστη: {user} - {status}")

# Αφαίρεση μηνυμάτων σφάλματος από το αρχείο m3u
with open("tiktok_live.m3u", "r") as m3u_file:
    lines = m3u_file.readlines()

with open("tiktok_live.m3u", "w") as m3u_file:
    for line in lines:
        if not line.startswith("error:"):
            m3u_file.write(line)
