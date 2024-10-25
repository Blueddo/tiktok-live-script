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
    "xara_xara_xara", "poparatsaklidou", "tzwrtzina_st", "kkonsta_ntina", "emy_has", "anastasiaa_official",
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
]

# Αφαίρεση διπλότυπων χρηστών
users = list(set(users))
print("Η λίστα των χρηστών χωρίς διπλότυπα δημιουργήθηκε")

# Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
m3u_filename = "tiktok_live.m3u"
with open(m3u_filename, "w") as m3u_file:
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
        with open(m3u_filename, "a") as m3u_file:
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
