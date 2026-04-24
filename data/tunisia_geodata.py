"""
Tunisia Geographic Data — Governorates, Delegations, and Secondary Schools.
Single source of truth for all location cascades in SSAS.
"""
from __future__ import annotations

# ── 24 Governorates → their official Delegations ────────────────────────────
GEODATA: dict[str, list[str]] = {
    "Tunis": [
        "Bab Bhar", "Bab Souika", "Carthage", "El Kabaria", "Ettahrir",
        "Ezzouhour", "Hraïria", "Jebel Jelloud", "Kram",
        "La Goulette", "La Marsa", "Le Bardo", "Médina",
        "Omrane Supérieur", "Ouardia", "Sidi El Béchir",
        "Sidi Hassine", "Sijoumi",
    ],
    "Ariana": [
        "Ariana Médina", "Ettadhamen", "Kalâat el-Andalous",
        "La Soukra", "Mnihla", "Raoued", "Sidi Thabet",
    ],
    "Ben Arous": [
        "Ben Arous", "Bou Mhel el-Bassatine", "El Mourouj", "Ezzahra",
        "Fouchana", "Hammam Chott", "Hammam Lif", "Medina Jedida",
        "Mohamedia", "Mornag", "Mégrine",
    ],
    "Manouba": [
        "Borj El Amri", "Djedeida", "Douar Hicher", "El Battane",
        "Manouba", "Oued Ellil", "Tebourba",
    ],
    "Nabeul": [
        "Beni Khalled", "Beni Khiar", "Bou Argoub",
        "Dar Chaâbane El Fehri", "El Haouaria", "El Mida",
        "Grombalia", "Hammam Ghezèze", "Hammamet",
        "Kélibia", "Korba", "Menzel Bouzelfa",
        "Menzel Temime", "Nabeul", "Soliman", "Takelsa",
    ],
    "Zaghouan": [
        "Bir Mcherga", "El Fahs", "Nadhour",
        "Saouaf", "Zaghouan", "Zriba",
    ],
    "Bizerte": [
        "Bizerte Nord", "Bizerte Sud", "El Alia", "Ghezala",
        "Ghar El Melh", "Joumine", "Mateur", "Menzel Bourguiba",
        "Menzel Jemil", "Ras Jebel", "Sejnane", "Tinja", "Utique",
    ],
    "Béja": [
        "Amdoun", "Béja Nord", "Béja Sud", "Goubellat",
        "Medjez el-Bab", "Nefza", "Testour", "Téboursouk", "Thibar",
    ],
    "Jendouba": [
        "Ain Draham", "Balta-Bou Aouane", "Bou Salem",
        "Fernana", "Ghardimaou", "Jendouba", "Jendouba Nord",
        "Oued Meliz", "Tabarka",
    ],
    "Kef": [
        "Dahmani", "Es Sers", "Kalâat Senan", "Kalâat Khasbat",
        "Kef Est", "Kef Ouest", "Ksour", "Nebeur",
        "Sakiet Sidi Youssef", "Tajerouine",
    ],
    "Siliana": [
        "Bargou", "Bou Arada", "El Aroussa", "El Krib", "Gaâfour",
        "Kesra", "Maktar", "Rouhia", "Sidi Bou Rouis",
        "Siliana Nord", "Siliana Sud",
    ],
    "Sousse": [
        "Akouda", "Bouficha", "Hammam Sousse", "Hergla",
        "Kalaa Kebira", "Kalaa Sghira", "Kondar", "M'saken",
        "Sidi Bou Ali", "Sidi El Heni",
        "Sousse Jawhara", "Sousse Médina",
        "Sousse Riadh", "Sousse Sidi Abdelhamid",
    ],
    "Monastir": [
        "Bekalta", "Bembla", "Beni Hassen", "Jammel",
        "Ksar Hellal", "Ksibet el-Médiouni", "Moknine",
        "Monastir", "Ouerdanine", "Sahline",
        "Sayada-Lamta-Bou Hajar", "Téboulba", "Zeramdine",
    ],
    "Mahdia": [
        "Bou Merdes", "Chebba", "Chorbane", "El Jem", "Essouassi",
        "Hjeïla", "Kerker", "Mahdia", "Melloulèche",
        "Ouled Chamekh", "Sidi Alouane",
    ],
    "Sfax": [
        "Agareb", "Bir Ali Ben Khalifa", "El Amra", "El Hencha",
        "Gremda", "Jebiniana", "Kerkenah", "Mahres",
        "Menzel Chaker", "Sakiet Eddaïer", "Sakiet Ezzit",
        "Sfax Est", "Sfax Médina", "Sfax Ouest", "Sfax Sud",
        "Skhira", "Thyna",
    ],
    "Kairouan": [
        "Bouhajla", "Chebika", "Chiriana", "El Alâa", "Haffouz",
        "Hajeb El Ayoun", "Kairouan Nord", "Kairouan Sud",
        "Nasrallah", "Oueslatia", "Sbikha",
    ],
    "Kasserine": [
        "Aïn Jedey", "Djedeliane", "El Ayoun", "Feriana",
        "Foussana", "Haïdra", "Hassi El Ferid",
        "Kasserine Nord", "Kasserine Sud",
        "Majel Bel Abbès", "Sbeitla", "Sbiba", "Thélepte",
    ],
    "Sidi Bouzid": [
        "Ben Aoun", "Bir El Hafey", "Cebbala-Sidi Aïch", "Jilma",
        "Mazzouna", "Meknassy", "Menzel Bouzaïane",
        "Ouled Haffouz", "Regueb",
        "Sidi Bouzid Est", "Sidi Bouzid Ouest", "Souk Jedid",
    ],
    "Gabès": [
        "El Hamma", "El Métouia", "Gabès Médina", "Gabès Ouest",
        "Gabès Sud", "Ghannouch", "Mareth", "Matmata",
        "Matmata Nouvelle", "Menzel El Habib",
    ],
    "Medenine": [
        "Ajim", "Ben Gardane", "Beni Khedache",
        "Djerba Ajim", "Djerba Houmt Souk", "Djerba Midoun",
        "Medenine Nord", "Medenine Sud", "Sidi Makhlouf", "Zarzis",
    ],
    "Tataouine": [
        "Bir Lahmar", "Dhiba", "Ghomrassen", "Remada",
        "Smar", "Tataouine Nord", "Tataouine Sud",
    ],
    "Gafsa": [
        "Belkhir", "El Guetar", "El Ksar",
        "Gafsa Nord", "Gafsa Sud", "Métlaoui",
        "Moulares", "Oum El Araies", "Redeyef", "Sened", "Sidi Aïch",
    ],
    "Tozeur": [
        "Degache", "Hazoua", "Nefta", "Tameghza", "Tozeur",
    ],
    "Kébili": [
        "Douz Nord", "Douz Sud", "El Faouar",
        "Kébili Nord", "Kébili Sud", "Souk El Ahed",
    ],
}

ALL_GOVERNORATES: list[str] = sorted(GEODATA.keys())
ALL_DELEGATIONS: list[str] = sorted(
    {d for dlist in GEODATA.values() for d in dlist}
)


def delegations_for_governorate(gov: str) -> list[str]:
    """Return sorted delegations for a given governorate name."""
    return sorted(GEODATA.get(gov, []))


# ── Lycées (Secondary Schools) by Delegation ────────────────────────────────
# Format: { delegation_name: [school_name, ...] }
LYCEES_BY_DELEGATION: dict[str, list[str]] = {
    # ── Tunis ────────────────────────────────────────────────────────────────
    "Jebel Jelloud": [
        "Lycée Jebel Jelloud",
        "Lycée Habib Thameur",
        "Lycée Ibn Khaldoun — Jebel Jelloud",
        "Lycée Ibn Sina — Jebel Jelloud",
    ],
    "Bab Bhar": [
        "Lycée Carnot",
        "Collège Sadiki",
        "Lycée Habib Bourguiba de Tunis",
        "Lycée 9 Avril 1938",
    ],
    "Médina": [
        "Lycée Khaznadar",
        "Lycée Al-Manar",
        "Lycée de la Médina",
    ],
    "La Marsa": [
        "Lycée La Marsa",
        "Lycée Marsa Plage",
        "Lycée La Marsa 2",
    ],
    "Le Bardo": [
        "Lycée du Bardo",
        "Lycée Habib Bourguiba du Bardo",
        "Lycée 25 Juillet — Bardo",
    ],
    "Carthage": [
        "Lycée de Carthage",
        "Lycée Hannibal — Carthage",
    ],
    "La Goulette": [
        "Lycée de La Goulette",
        "Lycée Ibn Rachiq — La Goulette",
    ],
    "El Kabaria": [
        "Lycée El Kabaria",
        "Lycée Ibn Sina — El Kabaria",
        "Lycée 7 Novembre — El Kabaria",
    ],
    "Sijoumi": [
        "Lycée Sijoumi",
        "Lycée Fattouma Bourguiba — Sijoumi",
    ],
    "Ettahrir": [
        "Lycée Ettahrir",
        "Lycée Mongi Slim",
    ],
    "Ezzouhour": [
        "Lycée Ezzouhour",
        "Lycée Tahar Haddad — Ezzouhour",
    ],
    "Hraïria": [
        "Lycée Hraïria",
    ],
    "Sidi El Béchir": [
        "Lycée Sidi El Béchir",
        "Lycée Habib Maâzoun",
    ],
    "Sidi Hassine": [
        "Lycée Sidi Hassine",
        "Lycée Ibn Nafis — Sidi Hassine",
    ],
    "Ouardia": [
        "Lycée Ouardia",
        "Lycée 18 Janvier — Ouardia",
    ],
    "Omrane Supérieur": [
        "Lycée Omrane Supérieur",
        "Lycée 15 Octobre — Omrane",
    ],
    "Kram": [
        "Lycée du Kram",
        "Lycée El Amel — Kram",
    ],
    # ── Ariana ───────────────────────────────────────────────────────────────
    "Ariana Médina": [
        "Lycée d'Ariana",
        "Lycée Mohamed Boudhina",
        "Lycée 20 Mars — Ariana",
    ],
    "Ettadhamen": [
        "Lycée Ettadhamen",
        "Lycée Ibn Charaf",
        "Lycée El Amal — Ettadhamen",
    ],
    "La Soukra": [
        "Lycée La Soukra",
        "Lycée Bourguiba de La Soukra",
    ],
    "Raoued": [
        "Lycée Raoued",
        "Lycée El Menzah — Raoued",
    ],
    "Mnihla": [
        "Lycée Mnihla",
    ],
    "Sidi Thabet": [
        "Lycée Sidi Thabet",
    ],
    "Kalâat el-Andalous": [
        "Lycée Kalâat el-Andalous",
    ],
    # ── Ben Arous ─────────────────────────────────────────────────────────────
    "Ben Arous": [
        "Lycée Ben Arous",
        "Lycée 20 Mars — Ben Arous",
        "Lycée Habib Bourguiba — Ben Arous",
    ],
    "El Mourouj": [
        "Lycée El Mourouj 1",
        "Lycée El Mourouj 2",
        "Lycée El Mourouj 3",
        "Lycée Kheireddine — El Mourouj",
    ],
    "Hammam Lif": [
        "Lycée Hammam Lif",
        "Lycée Ibn Rachiq",
        "Lycée 7 Novembre — Hammam Lif",
    ],
    "Ezzahra": [
        "Lycée Ezzahra",
        "Lycée Ibn Khaldoun — Ezzahra",
    ],
    "Mégrine": [
        "Lycée Mégrine",
        "Lycée Ibn Sina — Mégrine",
    ],
    "Hammam Chott": [
        "Lycée Hammam Chott",
    ],
    "Bou Mhel el-Bassatine": [
        "Lycée Bou Mhel el-Bassatine",
    ],
    "Fouchana": [
        "Lycée Fouchana",
    ],
    "Mornag": [
        "Lycée Mornag",
    ],
    # ── Manouba ───────────────────────────────────────────────────────────────
    "Manouba": [
        "Lycée de Manouba",
        "Lycée Habib Bourguiba de Manouba",
    ],
    "Oued Ellil": [
        "Lycée Oued Ellil",
        "Lycée El Amel — Oued Ellil",
    ],
    "Tebourba": [
        "Lycée Tebourba",
    ],
    "Douar Hicher": [
        "Lycée Douar Hicher",
        "Lycée Ibn Khaldoun — Douar Hicher",
    ],
    "Djedeida": [
        "Lycée Djedeida",
    ],
    # ── Nabeul ────────────────────────────────────────────────────────────────
    "Nabeul": [
        "Lycée de Nabeul",
        "Lycée Ibn Abi Dhiaf — Nabeul",
        "Lycée Azzouza Othmana",
        "Lycée 7 Novembre — Nabeul",
    ],
    "Hammamet": [
        "Lycée Hammamet",
        "Lycée El Yasmine — Hammamet",
        "Lycée Hammamet Sud",
    ],
    "Grombalia": [
        "Lycée Grombalia",
        "Lycée 25 Juillet — Grombalia",
    ],
    "Kélibia": [
        "Lycée Kélibia",
    ],
    "Korba": [
        "Lycée Korba",
    ],
    "Menzel Temime": [
        "Lycée Menzel Temime",
    ],
    "Soliman": [
        "Lycée Soliman",
    ],
    # ── Bizerte ───────────────────────────────────────────────────────────────
    "Bizerte Nord": [
        "Lycée Bizerte",
        "Lycée El Amel de Bizerte",
        "Lycée El Menzah de Bizerte",
        "Lycée Habib Bourguiba de Bizerte",
    ],
    "Bizerte Sud": [
        "Lycée Bizerte Sud",
        "Lycée Ibn Khaldoun — Bizerte",
    ],
    "Menzel Bourguiba": [
        "Lycée Menzel Bourguiba",
        "Lycée Farhat Hached — Menzel Bourguiba",
    ],
    "Ras Jebel": [
        "Lycée Ras Jebel",
    ],
    "Mateur": [
        "Lycée Mateur",
    ],
    "Sejnane": [
        "Lycée Sejnane",
    ],
    "Menzel Jemil": [
        "Lycée Menzel Jemil",
    ],
    # ── Béja ──────────────────────────────────────────────────────────────────
    "Béja Nord": [
        "Lycée de Béja",
        "Lycée Farhat Hached de Béja",
        "Lycée 7 Novembre — Béja",
    ],
    "Béja Sud": [
        "Lycée Béja Sud",
    ],
    "Medjez el-Bab": [
        "Lycée Medjez el-Bab",
    ],
    "Téboursouk": [
        "Lycée Téboursouk",
    ],
    "Testour": [
        "Lycée Testour",
    ],
    # ── Jendouba ──────────────────────────────────────────────────────────────
    "Jendouba": [
        "Lycée de Jendouba",
        "Lycée 7 Novembre — Jendouba",
        "Lycée Ibn Khaldoun — Jendouba",
    ],
    "Jendouba Nord": [
        "Lycée Jendouba Nord",
    ],
    "Tabarka": [
        "Lycée de Tabarka",
    ],
    "Ain Draham": [
        "Lycée Ain Draham",
    ],
    "Bou Salem": [
        "Lycée Bou Salem",
    ],
    "Ghardimaou": [
        "Lycée Ghardimaou",
    ],
    # ── Kef ───────────────────────────────────────────────────────────────────
    "Kef Est": [
        "Lycée du Kef",
        "Lycée Habib Bourguiba du Kef",
    ],
    "Kef Ouest": [
        "Lycée Kef Ouest",
    ],
    "Dahmani": [
        "Lycée Dahmani",
    ],
    "Tajerouine": [
        "Lycée Tajerouine",
    ],
    "Nebeur": [
        "Lycée Nebeur",
    ],
    # ── Siliana ───────────────────────────────────────────────────────────────
    "Siliana Nord": [
        "Lycée de Siliana",
        "Lycée Farhat Hached — Siliana",
    ],
    "Siliana Sud": [
        "Lycée Siliana Sud",
    ],
    "Maktar": [
        "Lycée Maktar",
    ],
    "Bou Arada": [
        "Lycée Bou Arada",
    ],
    # ── Sousse ────────────────────────────────────────────────────────────────
    "Sousse Médina": [
        "Lycée de Sousse",
        "Lycée 15 Novembre — Sousse",
        "Lycée Ibn Khaldoun — Sousse",
    ],
    "Sousse Jawhara": [
        "Lycée Sousse Jawhara",
        "Lycée El Manar — Sousse",
    ],
    "Sousse Riadh": [
        "Lycée Sousse Riadh",
    ],
    "Sousse Sidi Abdelhamid": [
        "Lycée Sidi Abdelhamid",
    ],
    "Hammam Sousse": [
        "Lycée Hammam Sousse",
        "Lycée 7 Novembre — Hammam Sousse",
    ],
    "Kalaa Kebira": [
        "Lycée Kalaa Kebira",
        "Lycée Ibn Rachiq — Kalaa Kebira",
    ],
    "M'saken": [
        "Lycée M'saken",
        "Lycée Sahloul",
    ],
    "Akouda": [
        "Lycée Akouda",
    ],
    "Bouficha": [
        "Lycée Bouficha",
    ],
    # ── Monastir ──────────────────────────────────────────────────────────────
    "Monastir": [
        "Lycée Monastir",
        "Lycée Ibn Khaldoun de Monastir",
        "Lycée 20 Mars — Monastir",
    ],
    "Ksar Hellal": [
        "Lycée Ksar Hellal",
        "Lycée Habib Bourguiba — Ksar Hellal",
    ],
    "Moknine": [
        "Lycée Moknine",
    ],
    "Jammel": [
        "Lycée Jammel",
    ],
    "Téboulba": [
        "Lycée Téboulba",
    ],
    "Zeramdine": [
        "Lycée Zeramdine",
    ],
    # ── Mahdia ────────────────────────────────────────────────────────────────
    "Mahdia": [
        "Lycée de Mahdia",
        "Lycée Habib Bourguiba — Mahdia",
        "Lycée El Amel — Mahdia",
    ],
    "El Jem": [
        "Lycée El Jem",
    ],
    "Chebba": [
        "Lycée Chebba",
    ],
    "Essouassi": [
        "Lycée Essouassi",
    ],
    # ── Sfax ──────────────────────────────────────────────────────────────────
    "Sfax Médina": [
        "Lycée de Sfax",
        "Lycée Habib Maâzoun de Sfax",
        "Lycée Ibn Khaldoun de Sfax",
        "Lycée 15 Novembre — Sfax",
    ],
    "Sfax Est": [
        "Lycée Sfax Est",
        "Lycée 7 Novembre — Sfax Est",
        "Lycée Ibn Sina — Sfax Est",
    ],
    "Sfax Ouest": [
        "Lycée Sfax Ouest",
        "Lycée Taïeb Mhiri — Sfax",
    ],
    "Sfax Sud": [
        "Lycée Sfax Sud",
    ],
    "Sakiet Eddaïer": [
        "Lycée Sakiet Eddaïer",
    ],
    "Sakiet Ezzit": [
        "Lycée Sakiet Ezzit",
    ],
    "Gremda": [
        "Lycée Gremda",
    ],
    "Agareb": [
        "Lycée Agareb",
    ],
    "El Hencha": [
        "Lycée El Hencha",
    ],
    "Mahres": [
        "Lycée Mahres",
    ],
    "Jebiniana": [
        "Lycée Jebiniana",
    ],
    # ── Kairouan ──────────────────────────────────────────────────────────────
    "Kairouan Nord": [
        "Lycée de Kairouan",
        "Lycée El Amel de Kairouan",
        "Lycée Ibn Rachiq — Kairouan",
        "Lycée 7 Novembre — Kairouan",
    ],
    "Kairouan Sud": [
        "Lycée Kairouan Sud",
    ],
    "Sbikha": [
        "Lycée Sbikha",
    ],
    "Haffouz": [
        "Lycée Haffouz",
    ],
    "El Alâa": [
        "Lycée El Alâa",
    ],
    "Hajeb El Ayoun": [
        "Lycée Hajeb El Ayoun",
    ],
    # ── Kasserine ─────────────────────────────────────────────────────────────
    "Kasserine Nord": [
        "Lycée de Kasserine",
        "Lycée Allal El Fassi de Kasserine",
        "Lycée 7 Novembre — Kasserine",
    ],
    "Kasserine Sud": [
        "Lycée Kasserine Sud",
    ],
    "Sbeitla": [
        "Lycée Sbeitla",
        "Lycée Farhat Hached — Sbeitla",
    ],
    "Feriana": [
        "Lycée Feriana",
    ],
    "Foussana": [
        "Lycée Foussana",
    ],
    # ── Sidi Bouzid ───────────────────────────────────────────────────────────
    "Sidi Bouzid Est": [
        "Lycée de Sidi Bouzid",
        "Lycée Farhat Hached — Sidi Bouzid",
        "Lycée 7 Novembre — Sidi Bouzid",
    ],
    "Sidi Bouzid Ouest": [
        "Lycée Sidi Bouzid Ouest",
    ],
    "Regueb": [
        "Lycée Regueb",
    ],
    "Meknassy": [
        "Lycée Meknassy",
    ],
    "Bir El Hafey": [
        "Lycée Bir El Hafey",
    ],
    # ── Gabès ─────────────────────────────────────────────────────────────────
    "Gabès Médina": [
        "Lycée de Gabès",
        "Lycée Ibn El Jazzar de Gabès",
        "Lycée 7 Novembre — Gabès",
        "Lycée Habib Bourguiba — Gabès",
    ],
    "Gabès Ouest": [
        "Lycée Gabès Ouest",
    ],
    "Gabès Sud": [
        "Lycée Gabès Sud",
    ],
    "El Hamma": [
        "Lycée El Hamma",
    ],
    "Mareth": [
        "Lycée Mareth",
    ],
    "Matmata": [
        "Lycée Matmata",
    ],
    "Ghannouch": [
        "Lycée Ghannouch",
    ],
    # ── Medenine ──────────────────────────────────────────────────────────────
    "Medenine Nord": [
        "Lycée de Medenine",
        "Lycée Habib Bourguiba — Medenine",
    ],
    "Medenine Sud": [
        "Lycée Medenine Sud",
    ],
    "Zarzis": [
        "Lycée Zarzis",
        "Lycée El Amel — Zarzis",
    ],
    "Djerba Houmt Souk": [
        "Lycée de Houmt Souk",
        "Lycée Ibn Rashiq — Djerba",
        "Lycée 7 Novembre — Djerba",
    ],
    "Djerba Midoun": [
        "Lycée Djerba Midoun",
    ],
    "Ben Gardane": [
        "Lycée Ben Gardane",
    ],
    "Beni Khedache": [
        "Lycée Beni Khedache",
    ],
    # ── Tataouine ─────────────────────────────────────────────────────────────
    "Tataouine Nord": [
        "Lycée de Tataouine",
        "Lycée 7 Novembre — Tataouine",
    ],
    "Tataouine Sud": [
        "Lycée Tataouine Sud",
    ],
    "Ghomrassen": [
        "Lycée Ghomrassen",
    ],
    "Remada": [
        "Lycée Remada",
    ],
    # ── Gafsa ─────────────────────────────────────────────────────────────────
    "Gafsa Nord": [
        "Lycée de Gafsa",
        "Lycée 7 Novembre de Gafsa",
        "Lycée Habib Bourguiba — Gafsa",
    ],
    "Gafsa Sud": [
        "Lycée Gafsa Sud",
    ],
    "Métlaoui": [
        "Lycée Métlaoui",
        "Lycée Ibn Khaldoun — Métlaoui",
    ],
    "Redeyef": [
        "Lycée Redeyef",
    ],
    "Moulares": [
        "Lycée Moulares",
    ],
    "El Guetar": [
        "Lycée El Guetar",
    ],
    "El Ksar": [
        "Lycée El Ksar — Gafsa",
    ],
    "Oum El Araies": [
        "Lycée Oum El Araies",
    ],
    # ── Tozeur ────────────────────────────────────────────────────────────────
    "Tozeur": [
        "Lycée de Tozeur",
        "Lycée Ibn Rachiq — Tozeur",
    ],
    "Nefta": [
        "Lycée Nefta",
    ],
    "Degache": [
        "Lycée Degache",
    ],
    # ── Kébili ────────────────────────────────────────────────────────────────
    "Kébili Nord": [
        "Lycée de Kébili",
        "Lycée Habib Bourguiba — Kébili",
    ],
    "Kébili Sud": [
        "Lycée Kébili Sud",
    ],
    "Douz Nord": [
        "Lycée Douz",
    ],
    "Souk El Ahed": [
        "Lycée Souk El Ahed",
    ],
}


def schools_for_delegation(delegation: str, level: str = "") -> list[str]:
    """Return secondary schools for a delegation (+ optional level filter)."""
    if level and level != "Secondary":
        return []
    return sorted(LYCEES_BY_DELEGATION.get(delegation, []))


ALL_SECONDARY_SCHOOLS: list[str] = sorted(
    {s for schools in LYCEES_BY_DELEGATION.values() for s in schools}
)
