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
    "Bab Bhar":     ["Lycée Carnot", "Lycée 9 Avril 1938", "Lycée Alaoui",
                     "Lycée Bab El Khadra"],
    "Médina":       ["Collège Sadiki", "Lycée Khaznadar", "Lycée Bourguiba",
                     "Lycée de la rue de Russie"],
    "Le Bardo":     ["Lycée du Bardo", "Lycée Pilote du Bardo",
                     "Lycée Hannibal — Le Bardo"],
    "Carthage":     ["Lycée de Carthage", "Lycée Pilote de Carthage Présidence",
                     "Lycée français MLF Pierre Mendès-France"],
    "La Marsa":     ["Lycée La Marsa", "Lycée Pilote La Marsa",
                     "Lycée Gustave Flaubert (français)"],
    "La Goulette":  ["Lycée de La Goulette", "Lycée Habib Thameur"],
    "El Kabaria":   ["Lycée El Kabaria 1", "Lycée El Kabaria 2"],
    "Jebel Jelloud":["Lycée Jebel Jelloud", "Lycée Hédi Chaker — Jebel Jelloud"],
    "Sijoumi":      ["Lycée Sijoumi", "Lycée Ibn Sina — Sijoumi"],
    "Ettahrir":     ["Lycée Ettahrir", "Lycée Ibn Rachiq — Ettahrir"],
    "Ezzouhour":    ["Lycée Ezzouhour 1", "Lycée Ezzouhour 2"],
    "Hraïria":      ["Lycée Hraïria", "Lycée Ali Belhouane — Hraïria"],
    "Sidi Hassine": ["Lycée Sidi Hassine", "Lycée Sidi Hassine Sijoumi"],
    "Omrane Supérieur": ["Lycée Omrane Supérieur", "Lycée Mongi Slim — Omrane"],
    "Kram":         ["Lycée du Kram", "Lycée Le Kram Ouest"],
    "Bab Souika":   ["Lycée Bab Souika", "Lycée Ibn Abi Dhiaf"],

    # ── Ariana ───────────────────────────────────────────────────────────────
    "Ariana Médina": ["Lycée d'Ariana", "Lycée Pilote Ariana",
                      "Lycée Ibn Charaf — El Menzah",
                      "Lycée El Menzah 6", "Lycée Habib Bourguiba — Ariana"],
    "Ettadhamen":    ["Lycée Ettadhamen 1", "Lycée Ettadhamen 2"],
    "La Soukra":     ["Lycée La Soukra", "Lycée Borj Louzir — La Soukra"],
    "Raoued":        ["Lycée Raoued", "Lycée Cité Ennasr — Raoued"],
    "Mnihla":        ["Lycée Mnihla", "Lycée Cité Ettadhamen"],
    "Sidi Thabet":   ["Lycée Sidi Thabet", "Lycée Borj Touil"],
    "Kalâat el-Andalous": ["Lycée Kalâat el-Andalous"],

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
    "Sousse Médina":  ["Lycée de Sousse", "Lycée Pilote de Sousse",
                       "Lycée Mohamed Ali Sousse", "Lycée Ibn Khaldoun Sousse"],
    "Sousse Riadh":   ["Lycée Sousse Riadh", "Lycée Khezama Sousse"],
    "Sousse Jawhara": ["Lycée Sousse Jawhara", "Lycée Cité Erriadh"],
    "Sousse Sidi Abdelhamid": ["Lycée Sidi Abdelhamid"],
    "Hammam Sousse":  ["Lycée Hammam Sousse", "Lycée 7 Novembre — Hammam Sousse"],
    "Kalaa Kebira":   ["Lycée Kalaa Kebira", "Lycée Habib Bourguiba — Kalaa Kebira"],
    "Kalaa Sghira":   ["Lycée Kalaa Sghira"],
    "M'saken":        ["Lycée M'saken 1", "Lycée M'saken 2"],
    "Akouda":         ["Lycée Akouda"],
    "Bouficha":       ["Lycée Bouficha"],
    "Hergla":         ["Lycée Hergla"],

    # ── Monastir ──────────────────────────────────────────────────────────────
    "Monastir":    ["Lycée de Monastir", "Lycée Pilote de Monastir",
                    "Lycée 2 Mars 1934 Monastir"],
    "Ksar Hellal": ["Lycée Ksar Hellal", "Lycée Ali Bourguiba — Ksar Hellal"],
    "Moknine":     ["Lycée Moknine", "Lycée Tahar Sfar — Moknine"],
    "Jammel":      ["Lycée Jammel"],
    "Téboulba":    ["Lycée Téboulba"],
    "Zeramdine":   ["Lycée Zeramdine"],
    "Bekalta":     ["Lycée Bekalta"],
    "Bembla":      ["Lycée Bembla"],
    "Sahline":     ["Lycée Sahline"],
    "Ksibet el-Médiouni": ["Lycée Ksibet el-Médiouni"],

    # ── Mahdia ────────────────────────────────────────────────────────────────
    "Mahdia":    ["Lycée de Mahdia", "Lycée Pilote de Mahdia",
                  "Lycée Tahar Sfar — Mahdia"],
    "El Jem":    ["Lycée El Jem", "Lycée Habib Bourguiba — El Jem"],
    "Chebba":    ["Lycée Chebba"],
    "Essouassi": ["Lycée Essouassi"],
    "Bou Merdes":["Lycée Bou Merdes"],
    "Ouled Chamekh": ["Lycée Ouled Chamekh"],

    # ── Sfax ──────────────────────────────────────────────────────────────────
    "Sfax Médina":    ["Lycée de Sfax", "Lycée Habib Maâzoun",
                       "Lycée Pilote Habib Bouguiba Sfax",
                       "Lycée Hédi Chaker — Sfax", "Lycée Mohamed Attia"],
    "Sfax Est":       ["Lycée Sfax Est", "Lycée Salah Eddine El Ayoubi"],
    "Sfax Ouest":     ["Lycée Sfax Ouest", "Lycée Cité El Habib"],
    "Sfax Sud":       ["Lycée Sfax Sud", "Lycée Thyna"],
    "Sakiet Eddaïer": ["Lycée Sakiet Eddaïer"],
    "Sakiet Ezzit":   ["Lycée Sakiet Ezzit"],
    "Gremda":         ["Lycée Gremda"],
    "Agareb":         ["Lycée Agareb"],
    "El Hencha":      ["Lycée El Hencha"],
    "Mahres":         ["Lycée Mahres"],
    "Jebiniana":      ["Lycée Jebiniana"],
    "Kerkenah":       ["Lycée Kerkenah"],
    "Bir Ali Ben Khalifa": ["Lycée Bir Ali Ben Khalifa"],
    "Skhira":         ["Lycée Skhira"],
    "Thyna":          ["Lycée Thyna"],

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


# ── Common Tunisian secondary-school name patterns ──────────────────────────
# Lycées in Tunisia are typically named after:
#   • the locality itself          → "Lycée <Delegation>"
#   • a national figure            → "Lycée Habib Bourguiba", "Lycée Ibn Khaldoun"
#   • a historical date            → "Lycée 2 Mars 1934", "Lycée 9 Avril 1938"
#   • the type of school           → "Lycée Pilote …", "Lycée Secondaire …"
# We use these patterns to surface 4-5 plausible options per delegation while
# keeping any hand-curated names from LYCEES_BY_DELEGATION first in the list.
_SCHOOL_SUFFIX_PATTERNS: list[str] = [
    "Lycée {d}",
    "Lycée Secondaire {d}",
    "Lycée Ibn Khaldoun — {d}",
    "Lycée Habib Bourguiba — {d}",
    "Lycée 2 Mars 1934 — {d}",
    "Lycée 9 Avril 1938 — {d}",
]
_PILOTE_GOVERNORATES: set[str] = set(GEODATA.keys())  # one Lycée Pilote per gov


def _generated_schools(delegation: str) -> list[str]:
    """Generate plausible school name candidates for a delegation."""
    return [pat.format(d=delegation) for pat in _SCHOOL_SUFFIX_PATTERNS]


def _governorate_for_delegation(delegation: str) -> str | None:
    for gov, dlist in GEODATA.items():
        if delegation in dlist:
            return gov
    return None


def _lycees_for(delegation: str) -> list[str]:
    """Internal: build the level=Secondary list (curated + Pilote + patterns)."""
    seen: dict[str, str] = {}
    out: list[str] = []

    def _push(name: str) -> None:
        key = name.strip().lower()
        if key and key not in seen:
            seen[key] = name
            out.append(name)

    for s in LYCEES_BY_DELEGATION.get(delegation, []):
        _push(s)
    gov = _governorate_for_delegation(delegation)
    if gov:
        _push(f"Lycée Pilote de {gov}")
    for s in _generated_schools(delegation):
        _push(s)
        if len(out) >= 8:
            break
    return out


# ── Collèges (Preparatory schools — 7e, 8e, 9e année) ───────────────────────
_COLLEGE_PATTERNS: list[str] = [
    "Collège {d}",
    "Collège Préparatoire {d}",
    "Collège Ibn Khaldoun — {d}",
    "Collège Habib Bourguiba — {d}",
    "Collège 7 Novembre — {d}",
]


def _colleges_for(delegation: str) -> list[str]:
    out = [pat.format(d=delegation) for pat in _COLLEGE_PATTERNS]
    gov = _governorate_for_delegation(delegation)
    if gov:
        out.append(f"Collège Pilote de {gov}")
    return out[:6]


# ── Écoles primaires (1re → 6e année) ───────────────────────────────────────
_PRIMARY_PATTERNS: list[str] = [
    "École Primaire {d} 1",
    "École Primaire {d} 2",
    "École Primaire Ibn Sina — {d}",
    "École Primaire Habib Bourguiba — {d}",
    "École Primaire 20 Mars — {d}",
    "École Primaire Tahar Haddad — {d}",
]


def _primaries_for(delegation: str) -> list[str]:
    return [pat.format(d=delegation) for pat in _PRIMARY_PATTERNS][:6]


# ── Universités tunisiennes (les 13 universités publiques + grandes écoles) ─
# Source : Ministère de l'Enseignement Supérieur et de la Recherche Scientifique
UNIVERSITIES_BY_GOVERNORATE: dict[str, list[str]] = {
    "Tunis": [
        "Université de Tunis",
        "Université Tunis El Manar",
        "Université Ez-Zitouna",
        "Université Virtuelle de Tunis",
        "ENIT — École Nationale d'Ingénieurs de Tunis",
        "INSAT — Institut National des Sciences Appliquées et de Technologie",
        "ESPRIT — École Supérieure Privée d'Ingénierie et de Technologies",
        "ISG Tunis — Institut Supérieur de Gestion",
        "FST — Faculté des Sciences de Tunis",
        "FMT — Faculté de Médecine de Tunis",
        "FSEG Tunis — Faculté des Sciences Économiques et de Gestion",
        "IPEIT — Institut Préparatoire aux Études d'Ingénieurs de Tunis",
        "ISI — Institut Supérieur d'Informatique",
        "ENSIT — École Nationale Supérieure d'Ingénieurs de Tunis",
        "ENSTAB — École Nationale Supérieure des Technologies Avancées",
    ],
    "Ariana": [
        "Université de Carthage",
        "ENSI — École Nationale des Sciences de l'Informatique (Manouba/Ariana)",
        "ESPRIT — École Supérieure Privée d'Ingénierie",
        "INSAT (campus)",
        "ISET Charguia",
    ],
    "Ben Arous": [
        "ISET Radès",
        "ENICarthage — École Nationale d'Ingénieurs de Carthage",
        "Faculté des Sciences Juridiques de Tunis (Ben Arous campus)",
    ],
    "Manouba": [
        "Université de la Manouba",
        "ENSI — École Nationale des Sciences de l'Informatique",
        "ISCAE — Institut Supérieur de Comptabilité et d'Administration des Entreprises",
        "ISD — Institut Supérieur de Documentation",
        "IPSI — Institut de Presse et des Sciences de l'Information",
    ],
    "Nabeul": [
        "IPEIN — Institut Préparatoire aux Études d'Ingénieurs de Nabeul",
        "ISET Nabeul",
        "ISSAT Mateur (annexe Nabeul)",
        "Faculté des Sciences Juridiques, Politiques et Sociales de Tunis (annexe Nabeul)",
    ],
    "Bizerte": [
        "Université de Carthage (campus Bizerte)",
        "IPEIB — Institut Préparatoire aux Études d'Ingénieurs de Bizerte",
        "ISSAT Mateur — Institut Supérieur des Sciences Appliquées et de Technologie",
        "ISET Bizerte",
        "Faculté des Sciences de Bizerte",
    ],
    "Sousse": [
        "Université de Sousse",
        "ENISO — École Nationale d'Ingénieurs de Sousse",
        "ISITCom — Institut Supérieur d'Informatique et des Techniques de Communication",
        "IPEIM (annexe Sousse)",
        "ISET Sousse",
        "Faculté de Médecine de Sousse",
        "Faculté de Droit et des Sciences Politiques de Sousse",
    ],
    "Monastir": [
        "Université de Monastir",
        "ENIM — École Nationale d'Ingénieurs de Monastir",
        "IPEIM — Institut Préparatoire aux Études d'Ingénieurs de Monastir",
        "ISET Ksar Hellal",
        "Faculté de Médecine de Monastir",
        "Faculté de Pharmacie de Monastir",
        "Faculté des Sciences de Monastir",
    ],
    "Mahdia": [
        "ISIMa — Institut Supérieur d'Informatique de Mahdia",
        "ISET Mahdia",
        "Faculté des Sciences Économiques et de Gestion de Mahdia",
    ],
    "Sfax": [
        "Université de Sfax",
        "ENIS — École Nationale d'Ingénieurs de Sfax",
        "IPEIS — Institut Préparatoire aux Études d'Ingénieurs de Sfax",
        "ISET Sfax",
        "FSEGS — Faculté des Sciences Économiques et de Gestion de Sfax",
        "FSS — Faculté des Sciences de Sfax",
        "Faculté de Médecine de Sfax",
        "ISGI — Institut Supérieur de Gestion Industrielle de Sfax",
    ],
    "Kairouan": [
        "Université de Kairouan",
        "IPEIK — Institut Préparatoire aux Études d'Ingénieurs de Kairouan",
        "ISIGK — Institut Supérieur d'Informatique et de Gestion de Kairouan",
        "ISET Kairouan",
        "Faculté de Charia et des Fondements de la Religion",
    ],
    "Kasserine": [
        "ISET Kasserine",
        "Faculté des Sciences et Techniques de Kasserine",
    ],
    "Sidi Bouzid": [
        "ISET Sidi Bouzid",
        "Institut Supérieur des Sciences Appliquées et de Technologie de Sidi Bouzid",
    ],
    "Gabès": [
        "Université de Gabès",
        "ENIG — École Nationale d'Ingénieurs de Gabès",
        "IPEIG — Institut Préparatoire aux Études d'Ingénieurs de Gabès",
        "ISET Gabès",
        "FSG — Faculté des Sciences de Gabès",
        "Faculté de Médecine de Gabès",
    ],
    "Medenine": [
        "ISET Djerba",
        "ISET Medenine",
        "Institut Supérieur des Études Appliquées en Humanités de Medenine",
    ],
    "Tataouine": [
        "ISET Tataouine",
    ],
    "Gafsa": [
        "Université de Gafsa",
        "IPEIG (annexe Gafsa)",
        "ISET Gafsa",
        "Faculté des Sciences de Gafsa",
        "Institut des Mines de Métlaoui",
    ],
    "Tozeur": [
        "ISET Tozeur",
        "Institut Supérieur des Études Appliquées en Humanités de Tozeur",
    ],
    "Kébili": [
        "ISET Kébili",
    ],
    "Béja": [
        "ISET Béja",
        "ESIM Béja — École Supérieure des Ingénieurs de Medjez el-Bab",
        "Institut Supérieur de Biotechnologie de Béja",
    ],
    "Jendouba": [
        "Université de Jendouba",
        "ISET Jendouba",
        "ESA Mograne — École Supérieure d'Agriculture",
        "Faculté des Sciences Juridiques, Économiques et de Gestion de Jendouba",
    ],
    "Kef": [
        "Faculté des Sciences et Techniques du Kef",
        "ISET Kef",
        "Institut Supérieur Agronomique du Kef",
    ],
    "Siliana": [
        "ISET Siliana",
    ],
    "Zaghouan": [
        "ISET Zaghouan",
    ],
}

ALL_UNIVERSITIES: list[str] = sorted(
    {u for ulist in UNIVERSITIES_BY_GOVERNORATE.values() for u in ulist}
)


def universities_for_governorate(gov: str) -> list[str]:
    """All universities/grandes écoles in a governorate."""
    return list(UNIVERSITIES_BY_GOVERNORATE.get(gov, []))


def universities_for_delegation(delegation: str) -> list[str]:
    """Universities = governorate-level. Returns all of the gov's institutions."""
    gov = _governorate_for_delegation(delegation)
    if not gov:
        return []
    return universities_for_governorate(gov)


def schools_for_delegation(delegation: str, level: str = "") -> list[str]:
    """Return relevant schools for a delegation, dispatched on educational level.

      • ""           → defaults to Secondary (lycées)
      • "Primary"    → écoles primaires
      • "Preparatory"→ collèges (7e, 8e, 9e)
      • "Secondary"  → lycées (4 ans : 1er année → bac)
      • "University" → universités + grandes écoles du gouvernorat
    """
    lvl = (level or "Secondary").strip()
    if lvl == "Primary":
        return _primaries_for(delegation)
    if lvl == "Preparatory":
        return _colleges_for(delegation)
    if lvl == "University":
        return universities_for_delegation(delegation)
    # Default & "Secondary"
    return _lycees_for(delegation)


ALL_SECONDARY_SCHOOLS: list[str] = sorted(
    {s for schools in LYCEES_BY_DELEGATION.values() for s in schools}
)
