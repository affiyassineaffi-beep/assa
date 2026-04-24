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
# Conservative, curated list — only lycées we have reasonable confidence
# really exist.  Each delegation ships at most the well-known landmark
# school(s); for everything else, the user types the school name freely
# in the registration / settings forms.  This list is intentionally short
# to avoid surfacing fabricated/invented school names.
LYCEES_BY_DELEGATION: dict[str, list[str]] = {
    # ── Tunis ────────────────────────────────────────────────────────────────
    "Bab Bhar":     ["Lycée Carnot", "Lycée 9 Avril 1938"],
    "Médina":       ["Collège Sadiki", "Lycée Khaznadar"],
    "Le Bardo":     ["Lycée du Bardo"],
    "Carthage":     ["Lycée de Carthage"],
    "La Marsa":     ["Lycée La Marsa"],
    "La Goulette":  ["Lycée de La Goulette"],
    "El Kabaria":   ["Lycée El Kabaria"],
    "Jebel Jelloud":["Lycée Jebel Jelloud"],
    "Sijoumi":      ["Lycée Sijoumi"],
    "Ettahrir":     ["Lycée Ettahrir"],
    "Ezzouhour":    ["Lycée Ezzouhour"],
    "Hraïria":      ["Lycée Hraïria"],
    "Sidi Hassine": ["Lycée Sidi Hassine"],
    "Omrane Supérieur": ["Lycée Omrane Supérieur"],
    "Kram":         ["Lycée du Kram"],

    # ── Ariana ───────────────────────────────────────────────────────────────
    "Ariana Médina": ["Lycée d'Ariana"],
    "Ettadhamen":    ["Lycée Ettadhamen"],
    "La Soukra":     ["Lycée La Soukra"],
    "Raoued":        ["Lycée Raoued"],
    "Mnihla":        ["Lycée Mnihla"],
    "Sidi Thabet":   ["Lycée Sidi Thabet"],

    # ── Ben Arous ─────────────────────────────────────────────────────────────
    "Ben Arous":   ["Lycée Ben Arous"],
    "El Mourouj":  ["Lycée El Mourouj 1", "Lycée El Mourouj 2"],
    "Hammam Lif":  ["Lycée Hammam Lif"],
    "Ezzahra":     ["Lycée Ezzahra"],
    "Mégrine":     ["Lycée Mégrine"],
    "Hammam Chott":["Lycée Hammam Chott"],
    "Fouchana":    ["Lycée Fouchana"],
    "Mornag":      ["Lycée Mornag"],

    # ── Manouba ───────────────────────────────────────────────────────────────
    "Manouba":      ["Lycée de Manouba"],
    "Oued Ellil":   ["Lycée Oued Ellil"],
    "Tebourba":     ["Lycée Tebourba"],
    "Douar Hicher": ["Lycée Douar Hicher"],
    "Djedeida":     ["Lycée Djedeida"],

    # ── Nabeul ────────────────────────────────────────────────────────────────
    "Nabeul":        ["Lycée de Nabeul"],
    "Hammamet":      ["Lycée Hammamet"],
    "Grombalia":     ["Lycée Grombalia"],
    "Kélibia":       ["Lycée Kélibia"],
    "Korba":         ["Lycée Korba"],
    "Menzel Temime": ["Lycée Menzel Temime"],
    "Soliman":       ["Lycée Soliman"],

    # ── Bizerte ───────────────────────────────────────────────────────────────
    "Bizerte Nord":     ["Lycée de Bizerte"],
    "Bizerte Sud":      ["Lycée Bizerte Sud"],
    "Menzel Bourguiba": ["Lycée Menzel Bourguiba"],
    "Ras Jebel":        ["Lycée Ras Jebel"],
    "Mateur":           ["Lycée Mateur"],
    "Sejnane":          ["Lycée Sejnane"],
    "Menzel Jemil":     ["Lycée Menzel Jemil"],

    # ── Béja ──────────────────────────────────────────────────────────────────
    "Béja Nord":     ["Lycée de Béja"],
    "Béja Sud":      ["Lycée Béja Sud"],
    "Medjez el-Bab": ["Lycée Medjez el-Bab"],
    "Téboursouk":    ["Lycée Téboursouk"],
    "Testour":       ["Lycée Testour"],

    # ── Jendouba ──────────────────────────────────────────────────────────────
    "Jendouba":   ["Lycée de Jendouba"],
    "Tabarka":    ["Lycée de Tabarka"],
    "Ain Draham": ["Lycée Ain Draham"],
    "Bou Salem":  ["Lycée Bou Salem"],
    "Ghardimaou": ["Lycée Ghardimaou"],

    # ── Kef ───────────────────────────────────────────────────────────────────
    "Kef Est":    ["Lycée du Kef"],
    "Kef Ouest":  ["Lycée Kef Ouest"],
    "Dahmani":    ["Lycée Dahmani"],
    "Tajerouine": ["Lycée Tajerouine"],

    # ── Siliana ───────────────────────────────────────────────────────────────
    "Siliana Nord": ["Lycée de Siliana"],
    "Maktar":       ["Lycée Maktar"],
    "Bou Arada":    ["Lycée Bou Arada"],

    # ── Sousse ────────────────────────────────────────────────────────────────
    "Sousse Médina":  ["Lycée de Sousse"],
    "Sousse Riadh":   ["Lycée Sousse Riadh"],
    "Hammam Sousse":  ["Lycée Hammam Sousse"],
    "Kalaa Kebira":   ["Lycée Kalaa Kebira"],
    "M'saken":        ["Lycée M'saken"],
    "Akouda":         ["Lycée Akouda"],
    "Bouficha":       ["Lycée Bouficha"],

    # ── Monastir ──────────────────────────────────────────────────────────────
    "Monastir":    ["Lycée de Monastir"],
    "Ksar Hellal": ["Lycée Ksar Hellal"],
    "Moknine":     ["Lycée Moknine"],
    "Jammel":      ["Lycée Jammel"],
    "Téboulba":    ["Lycée Téboulba"],
    "Zeramdine":   ["Lycée Zeramdine"],

    # ── Mahdia ────────────────────────────────────────────────────────────────
    "Mahdia":    ["Lycée de Mahdia"],
    "El Jem":    ["Lycée El Jem"],
    "Chebba":    ["Lycée Chebba"],
    "Essouassi": ["Lycée Essouassi"],

    # ── Sfax ──────────────────────────────────────────────────────────────────
    "Sfax Médina":    ["Lycée de Sfax", "Lycée Habib Maâzoun"],
    "Sfax Est":       ["Lycée Sfax Est"],
    "Sfax Ouest":     ["Lycée Sfax Ouest"],
    "Sfax Sud":       ["Lycée Sfax Sud"],
    "Sakiet Eddaïer": ["Lycée Sakiet Eddaïer"],
    "Sakiet Ezzit":   ["Lycée Sakiet Ezzit"],
    "Gremda":         ["Lycée Gremda"],
    "Agareb":         ["Lycée Agareb"],
    "El Hencha":      ["Lycée El Hencha"],
    "Mahres":         ["Lycée Mahres"],
    "Jebiniana":      ["Lycée Jebiniana"],

    # ── Kairouan ──────────────────────────────────────────────────────────────
    "Kairouan Nord":  ["Lycée de Kairouan"],
    "Kairouan Sud":   ["Lycée Kairouan Sud"],
    "Sbikha":         ["Lycée Sbikha"],
    "Haffouz":        ["Lycée Haffouz"],
    "Hajeb El Ayoun": ["Lycée Hajeb El Ayoun"],

    # ── Kasserine ─────────────────────────────────────────────────────────────
    "Kasserine Nord": ["Lycée de Kasserine"],
    "Kasserine Sud":  ["Lycée Kasserine Sud"],
    "Sbeitla":        ["Lycée Sbeitla"],
    "Feriana":        ["Lycée Feriana"],
    "Foussana":       ["Lycée Foussana"],

    # ── Sidi Bouzid ───────────────────────────────────────────────────────────
    "Sidi Bouzid Est":   ["Lycée de Sidi Bouzid"],
    "Sidi Bouzid Ouest": ["Lycée Sidi Bouzid Ouest"],
    "Regueb":            ["Lycée Regueb"],
    "Meknassy":          ["Lycée Meknassy"],
    "Bir El Hafey":      ["Lycée Bir El Hafey"],

    # ── Gabès ─────────────────────────────────────────────────────────────────
    "Gabès Médina": ["Lycée de Gabès"],
    "Gabès Ouest":  ["Lycée Gabès Ouest"],
    "Gabès Sud":    ["Lycée Gabès Sud"],
    "El Hamma":     ["Lycée El Hamma"],
    "Mareth":       ["Lycée Mareth"],
    "Matmata":      ["Lycée Matmata"],
    "Ghannouch":    ["Lycée Ghannouch"],

    # ── Medenine ──────────────────────────────────────────────────────────────
    "Medenine Nord":     ["Lycée de Medenine"],
    "Medenine Sud":      ["Lycée Medenine Sud"],
    "Zarzis":            ["Lycée Zarzis"],
    "Djerba Houmt Souk": ["Lycée de Houmt Souk"],
    "Djerba Midoun":     ["Lycée Djerba Midoun"],
    "Ben Gardane":       ["Lycée Ben Gardane"],
    "Beni Khedache":     ["Lycée Beni Khedache"],

    # ── Tataouine ─────────────────────────────────────────────────────────────
    "Tataouine Nord": ["Lycée de Tataouine"],
    "Tataouine Sud":  ["Lycée Tataouine Sud"],
    "Ghomrassen":     ["Lycée Ghomrassen"],
    "Remada":         ["Lycée Remada"],

    # ── Gafsa ─────────────────────────────────────────────────────────────────
    "Gafsa Nord":     ["Lycée de Gafsa"],
    "Gafsa Sud":      ["Lycée Gafsa Sud"],
    "Métlaoui":       ["Lycée Métlaoui"],
    "Redeyef":        ["Lycée Redeyef"],
    "Moulares":       ["Lycée Moulares"],
    "El Guetar":      ["Lycée El Guetar"],
    "El Ksar":        ["Lycée El Ksar"],
    "Oum El Araies":  ["Lycée Oum El Araies"],

    # ── Tozeur ────────────────────────────────────────────────────────────────
    "Tozeur":  ["Lycée de Tozeur"],
    "Nefta":   ["Lycée Nefta"],
    "Degache": ["Lycée Degache"],

    # ── Kébili ────────────────────────────────────────────────────────────────
    "Kébili Nord":  ["Lycée de Kébili"],
    "Kébili Sud":   ["Lycée Kébili Sud"],
    "Douz Nord":    ["Lycée Douz"],
    "Souk El Ahed": ["Lycée Souk El Ahed"],
}


def schools_for_delegation(delegation: str, level: str = "") -> list[str]:
    """Return secondary schools for a delegation (+ optional level filter)."""
    if level and level != "Secondary":
        return []
    return sorted(LYCEES_BY_DELEGATION.get(delegation, []))


ALL_SECONDARY_SCHOOLS: list[str] = sorted(
    {s for schools in LYCEES_BY_DELEGATION.values() for s in schools}
)
