@echo off
setlocal enabledelayedexpansion

rem Ορισμός χρηστών TikTok
set users=dwroula0 haroula_taotao valentiniro angelos.bam koemtzidoyyyy paraskeuopouloy kondyliam mariasofikiti0 ioannakoulouri180 viva.camper esperanzavanlife ioannistserkis78 tzervoudakis lazaros.a.avramidis ts0plakix freskia.zymi georgeporfiris zaxaroplastisa liros_zaxaroplastiki ibadam77 viktoria123_40 evgenis_smusenok aggelikimanousaki sto_pi_k_fi tustok _______jr_______ chris.fintr marwmaroy kaiti1959 sweetcookiemy krifes_alithies orinimelissa grintelas.com stauroulatheoxari jennakivl mirela_kondi vasilikigrn mariaaaxsl valentiniro kwnstantina.35 tasospapadopoulo angelstathis ariadni.mi elenimekolli17 sindika83 nikosgiko glorioustheoc basiliki_makri billiardgr user9333815415701 konstantina.loventina mimi.m1m1ka harman_gr 8meowkat8 vasiazouganeli giannelis_ klwntia_anna sofia_peridi journalist_presenter89 jrramonas vasalos_konstantinos vaggelitsa.kol grandfather_handmade ziogasantonis vivianavramidou sophiazoezitsis filiolou magic_vesto national_star_antreoulis seminarecipes.gr passailmintinoglou petrakosthess leonidas_bakery six_senses_candles2 georgegiannak piece.of.mam marymary___1 retsamaria442 ngradiogr aristea_alexandrakh panagiotis_milas edeirini anonymous_hacking_team pimenidisfilipos lenazevgara_official johnathan_stef orizontasgegonota nasia_ev nikos_parlantzas efi_gkouli96official vasilikibotsa besianahsj elena_charalampoudi potsepistasos nasia_ev katerinawhybe petronela_birsilaoff kostaspal82 thegreekmasterchef kkjewelry1 irinious1 eirinikalika sertsas ilias_kiazoli mydatingexperience2 user91618478129743 poparatsaklidou koemtzidoyyyy

rem Δημιουργία αρχείου m3u με επιπλέον πληροφορίες
echo #EXTM3U $BorpasFileFormat="1" $NestedGroupsSeparator="/" > tiktok_live.m3u
echo Σφάλματα Streamlink > errors.log

rem Έλεγχος για κάθε χρήστη αν είναι live
for %%u in (%users%) do (
    rem Χρησιμοποίησε το Streamlink για να ελέγξεις αν ο χρήστης είναι live
    for /f "tokens=*" %%a in ('streamlink https://www.tiktok.com/@%%u best --stream-url 2^>^&1') do (
        if not "%%a"=="error: No playable streams found on this URL: https://www.tiktok.com/@%%u" (
            if "!%%a:~0,5!" neq "error" (
                echo #EXTINF:-1 group-title="TikTok Live" tvg-logo="https://www.tiktok.com/favicon.ico" tvg-id="simpleTVFakeEpgId" $ExtFilter="Tikitok live",%%u >> tiktok_live.m3u
                echo %%a >> tiktok_live.m3u
            ) else (
                echo %%a >> errors.log
            )
        )
    )
)

echo Η λίστα m3u δημιουργήθηκε.
pause
