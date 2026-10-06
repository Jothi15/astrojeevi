import swisseph as swe

RASI_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

GRAHA_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Classical rasi rulers, index 0=Aries..11=Pisces. Rahu/Ketu rule no sign classically.
RASI_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]

MOVABLE_RASIS = {0, 3, 6, 9}
FIXED_RASIS = {1, 4, 7, 10}
DUAL_RASIS = {2, 5, 8, 11}

# Node: Mean Node, not True Node — matches classical Vedic dasa/yoga conventions
# (smooth retrograde motion vs. True Node's brief prograde loops).
NODE_MODE = swe.MEAN_NODE

EPHEMERIS_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

DASA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

DASA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}

DASA_LEVELS = ["mahadasa", "antardasa", "antaram", "sookshma", "prana"]

TARA_CATEGORIES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyak",
    "Sadhaka", "Vadha", "Mitra", "Ati-Mitra",
]

TARA_QUALITY = {
    "Janma": "neutral", "Sampat": "good", "Vipat": "bad", "Kshema": "good",
    "Pratyak": "bad", "Sadhaka": "good", "Vadha": "bad", "Mitra": "good", "Ati-Mitra": "good",
}

# Mandi/Gulika: which of the 8 day (or night) segments belongs to Saturn, by weekday
# (Sunday=0..Saturday=6). Day table decreases 7->1 across the week; the night table
# is derived from the classical "5th weekday forward" rule and comes out equally
# clean (3,2,1,7,6,5,4) — see app/upagraha.py for the full derivation/sources.
SATURN_DAY_SEGMENT = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
SATURN_NIGHT_SEGMENT = {0: 3, 1: 2, 2: 1, 3: 7, 4: 6, 5: 5, 6: 4}

# Indu Lagna: Kala (numeric value) of each of the 7 classical grahas; Rahu/Ketu
# aren't used. Cross-checked against two independent sources before use.
INDU_KALA = {"Sun": 30, "Moon": 16, "Mars": 6, "Mercury": 8, "Jupiter": 10, "Venus": 12, "Saturn": 1}

# Dignity: planet -> (exaltation rasi, debilitation rasi, deep exaltation degree).
# Debilitation is the opposite sign at the same degree. Rahu/Ketu follow the BPHS
# reading (Rahu exalted Taurus, Ketu exalted Scorpio); other traditions differ
# (e.g. Gemini/Sagittarius) so they have no agreed deep degree.
DIGNITY = {
    "Sun": (0, 6, 10.0),
    "Moon": (1, 7, 3.0),
    "Mars": (9, 3, 28.0),
    "Mercury": (5, 11, 15.0),
    "Jupiter": (3, 9, 5.0),
    "Venus": (11, 5, 27.0),
    "Saturn": (6, 0, 20.0),
    "Rahu": (1, 7, None),
    "Ketu": (7, 1, None),
}

# Pancha Mahapurusha yogas: planet -> (yoga name, own-sign rasis, exaltation rasi).
# The yoga forms when the planet is in its own or exaltation sign AND in a kendra.
# Rasi indices: 0=Aries..11=Pisces. Cross-checked against three sources.
PANCHA_MAHAPURUSHA = {
    "Mars": ("Ruchaka Yoga", {0, 7}, 9),
    "Mercury": ("Bhadra Yoga", {2, 5}, 5),
    "Jupiter": ("Hamsa Yoga", {8, 11}, 3),
    "Venus": ("Malavya Yoga", {1, 6}, 11),
    "Saturn": ("Sasa Yoga", {9, 10}, 6),
}

# Pushkara Navamsa: element of each rasi, index 0=Aries..11=Pisces.
RASI_ELEMENTS = ["fire", "earth", "air", "water"] * 3

# Which 2 of the 9 navamsa divisions (0-indexed part number) are Pushkara for
# each element. Cross-checked against two sources and independently re-derived
# from the app's own d9_navamsa formula (the degree ranges the sources give
# match exactly) — see conversation history for the derivation.
PUSHKARA_NAVAMSA_PARTS = {
    "fire": {6, 8},
    "earth": {2, 4},
    "air": {5, 7},
    "water": {0, 2},
}

# Thithi Soonyam: tithi number within its paksha (1=Prathamai..14=Chaturdasi) ->
# the rasis that tithi makes "void". Same table for both pakshas; Pournami and
# Amavasai (15) have none. Cross-checked against two sources, and the pattern
# matches a third's description (mostly 4th/10th pairs; Tritiyai and Saptami
# 6/8; Shashti 5/9; Chaturdasi all four dual signs).
THITHI_SOONYA_RASIS = {
    1: (6, 9),
    2: (8, 11),
    3: (4, 9),
    4: (1, 10),
    5: (2, 5),
    6: (0, 4),
    7: (3, 8),
    8: (2, 5),
    9: (4, 7),
    10: (4, 7),
    11: (8, 11),
    12: (6, 9),
    13: (1, 4),
    14: (2, 5, 8, 11),
}

# Kaala Pakai: the D1 rasis a graha is said to be at odds with (0=Aries..11=Pisces).
# As given by the user from a video; no written source. Ketu has none, and no graha
# has Leo.
KAALA_PAKAI_RASIS = {
    "Moon": (0, 1),
    "Rahu": (2,),
    "Sun": (3,),
    "Mars": (5,),
    "Jupiter": (6, 7),
    "Mercury": (8,),
    "Venus": (9, 10),
    "Saturn": (11,),
}

# Moorthi Nirnayam: count from the janma rasi to the Moon's rasi at a peyarchi
# (janma rasi = 1) -> Moorthi. Swarna is best, then Rajatha, Thamira, Loha. From
# astroshala.com's Moorti Nirnaya article.
MOORTHI_BY_COUNT = {
    1: "Swarna", 6: "Swarna", 11: "Swarna",
    2: "Rajatha", 5: "Rajatha", 9: "Rajatha",
    3: "Thamira", 7: "Thamira", 10: "Thamira",
    4: "Loha", 8: "Loha", 12: "Loha",
}

# The peyarchi window shown: 2026 and the next five years.
PEYARCHI_START_YEAR = 2026
PEYARCHI_END_YEAR = 2031
