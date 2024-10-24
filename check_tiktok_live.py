import os
import subprocess

# Ορισμός χρηστών TikTok
users = [
    "mainandros2", "viktoria123_40", "staurisgianopoulo", "orinimelissa", "to_moviesroom", "_______jr_______",
    "myrtw39", "dwroula0", "eni.umi77", "aurora__one", "karidomanna", "efi_gkouli96official", "mariasofikiti0",
    "emmanouil_konnstantinos", "xanthoaggeloudi", "boukitses", "valentiniro", "grintelas.com", "kaiti1959",
    "despoina_dim_", "moonstone.gr", "viva.camper", "leonidas_bakery", "kapetannis", "seminarecipes.gr",
    "chris.fintr", "lazaros.a.avramidis", "eosforos_._666", "zoi808", "levonleon1996", "esperanzavanlife",
    "koemtzidoyyyy", "candles.and.events", "chris_magic_mountain_", "kkjewelry1", "steve_ant",
    "mairi_mihoy_official", "mydatingexperience2", "ioannistserkis78", "pounentism", "maria.aristopoulo45",
    "xara_xara_xara", "poparatsaklidou", "tzwrtzina_st", "kkonsta_ntina", "emy_has.anastasiaa_official",
    "nicolkass_", "user5376357754610", "andronikinikaki", "nina_bodokia", "haroula_taotao", "karydaki_land",
    "jimpr2grivakis", "akadimia_ygeias", "gkounaki.elena", "mari_sweet_and_cake", "d0nalduck7", "irinious1",
    "eirini_psychologi", "panagiotis_milas", "xristosdimitroulis", "eephydatia", "antreastisi",
    "stefania_greece_4", "angelos.bam", "angelos.bam2", "pavlos_sfetsas", "nemesis3a", "paraskeuopoulo",
    "kondyliam", "stauroulatheoxari", "ioannakoulouri180", "kathxhtiko", "sertsas", "tzervoudakis",
    "lorenanikolla", "despoinabarka4", "freskia.zymi", "georgeporfiris", "zaxaroplastisa", "liros_zaxaroplastiki",
    "ibadam77", "kokkinosskoufos_skg", "evgenis_smusenok", "aggelikimanousaki", "sto_pi_k_fi", "tustok",
    "venetvlive", "gwgwdimou", "marwmaroy", "giannispapasifakis1", "krifes_alithies", "jennakivl", "mirela_kondi",
    "kostaspal1982", "angelstathis", "ariadni.mi", "sindika83", "nikosgiko", "glorioustheoc", "basiliki_makri",
    "billiardgr", "user9333815415701", "konstantina.loventina", "mimi.m1m1ka", "giannelis_", "klwntia_anna",
    "sofia_peridi", "vasalos_konstantinos", "vaggelitsa.kol", "ziogasantonis", "vivianavramidou", "sophiazoezitsis",
    "filiolou", "magic_vesto", "national_star_antreoulis", "passailmintinoglou", "petrakosthess",
    "six_senses_candles2", "georgegiannak", "dianaviopoulo", "retsamaria442", "ngradiogr", "aristea_alexandrakh",
    "kalliopifen1", "edeirini", "pimenidisfilipos", "lenazevgara_official", "johnathan_stef", "nasia_ev",
    "nikos_parlantzas", "vasilikibotsa", "besianahsj", "elena_charalampoudi", "potsepistasos", "katerinawhybe",
    "petronela_birsilaoff", "kostaspal82", "eirinikalika", "evita4040", "user91618478129743", "amaliakwstaraa",
    "saliagos.nikos", "xristinadiak", "focusfm103.6", "agapisartdesign", "pocahontas__._"

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
with open("tiktok_liveTEST.m3u", "w") as m3u_file:
    m3u_file.write("#EXTM3U $BorpasFileFormat=\"1\" $NestedGroupsSeparator=\"/\"\n")

# Έλεγχος για κάθε χρήστη αν είναι live
for user in users:
    result = subprocess.run(
        ["streamlink", f"https://www.tiktok.com/@{user}", "worst", "--stream-url"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    
    if "error: No playable streams found on this URL" not in output:
        if output.startswith("https://pull-f5-tt03.fcdn.eu.tiktokcdn.com/stage/stream-"):
            with open("tiktok_liveTEST.m3u", "a") as m3u_file:
                m3u_file.write(f"#EXTINF:-1 group-title=\"TikTok Live\" tvg-logo=\"https://www.tiktok.com/favicon.ico\" tvg-id=\"simpleTVFakeEpgId\" $ExtFilter=\"Tikitok live\",{user}\n")
                m3u_file.write(f"{output}\n")

# Αφαίρεση μηνυμάτων σφάλματος από το αρχείο m3u
with open("tiktok_liveTEST.m3u", "r") as m3u_file:
    lines = m3u_file.readlines()

with open("tiktok_liveTEST.m3u", "w") as m3u_file:
    for line in lines:
        if not line.startswith("error:"):
            m3u_file.write(line)
            
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
    else:
        print("Το αρχείο tiktok_live.m3u δεν βρέθηκε. Δεν έγινε καμία προώθηση στο GitHub.")
