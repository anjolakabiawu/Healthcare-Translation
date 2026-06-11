"""
Extended medical pronunciation dictionary.

The single most important asset in the pronunciation layer: a hand-curated
map of medical terms to their correct IPA, a simplified readable guide,
syllable breakdown, and stress pattern. Standard G2P engines mangle most of
these, so this dictionary takes priority over any automatic fallback.

Each entry:
    "ipa":        narrow-ish IPA transcription, slashes included
    "simplified": readable guide, stressed syllables in CAPS (e.g. a-TOR-va-sta-tin)
    "syllables":  list of syllables in reading order
    "stress":     1-based indices of stressed syllables within `syllables`
    "category":   drug | anatomy | condition | procedure  (for stats/grouping)

Keys are always lowercase. Look-ups must be case-insensitive.
"""

MEDICAL_DICT = {
    # ── Drugs ────────────────────────────────────────────────────────────
    "atorvastatin": {
        "ipa": "/eɪˌtɔːrvəˈstætɪn/",
        "simplified": "ay-TOR-va-STA-tin",
        "syllables": ["ay", "TOR", "va", "STA", "tin"],
        "stress": [2, 4],
        "category": "drug",
    },
    "metformin": {
        "ipa": "/mɛtˈfɔːrmɪn/",
        "simplified": "met-FOR-min",
        "syllables": ["met", "FOR", "min"],
        "stress": [2],
        "category": "drug",
    },
    "lisinopril": {
        "ipa": "/laɪˈsɪnəprɪl/",
        "simplified": "ly-SIN-o-pril",
        "syllables": ["ly", "SIN", "o", "pril"],
        "stress": [2],
        "category": "drug",
    },
    "omeprazole": {
        "ipa": "/oʊˈmɛprəzoʊl/",
        "simplified": "oh-MEP-ra-zole",
        "syllables": ["oh", "MEP", "ra", "zole"],
        "stress": [2],
        "category": "drug",
    },
    "azithromycin": {
        "ipa": "/əˌzɪθroʊˈmaɪsɪn/",
        "simplified": "a-ZITH-ro-MY-sin",
        "syllables": ["a", "ZITH", "ro", "MY", "sin"],
        "stress": [2, 4],
        "category": "drug",
    },
    "hydrochlorothiazide": {
        "ipa": "/ˌhaɪdroʊˌklɔːroʊˈθaɪəzaɪd/",
        "simplified": "HY-dro-KLOR-o-THY-a-zide",
        "syllables": ["HY", "dro", "KLOR", "o", "THY", "a", "zide"],
        "stress": [1, 3, 5],
        "category": "drug",
    },
    "amoxicillin": {
        "ipa": "/əˌmɒksɪˈsɪlɪn/",
        "simplified": "a-MOX-i-SIL-lin",
        "syllables": ["a", "MOX", "i", "SIL", "lin"],
        "stress": [2, 4],
        "category": "drug",
    },
    "metoprolol": {
        "ipa": "/mɛˈtoʊprəlɒl/",
        "simplified": "me-TOP-ro-lol",
        "syllables": ["me", "TOP", "ro", "lol"],
        "stress": [2],
        "category": "drug",
    },
    "levothyroxine": {
        "ipa": "/ˌliːvoʊθaɪˈrɒksiːn/",
        "simplified": "LEE-vo-thy-ROX-een",
        "syllables": ["LEE", "vo", "thy", "ROX", "een"],
        "stress": [1, 4],
        "category": "drug",
    },
    "gabapentin": {
        "ipa": "/ˌɡæbəˈpɛntɪn/",
        "simplified": "GAB-a-PEN-tin",
        "syllables": ["GAB", "a", "PEN", "tin"],
        "stress": [1, 3],
        "category": "drug",
    },
    "prednisone": {
        "ipa": "/ˈprɛdnɪsoʊn/",
        "simplified": "PRED-ni-sone",
        "syllables": ["PRED", "ni", "sone"],
        "stress": [1],
        "category": "drug",
    },
    "warfarin": {
        "ipa": "/ˈwɔːrfərɪn/",
        "simplified": "WAR-fa-rin",
        "syllables": ["WAR", "fa", "rin"],
        "stress": [1],
        "category": "drug",
    },
    "clopidogrel": {
        "ipa": "/kloʊˈpɪdoʊɡrɛl/",
        "simplified": "klo-PID-o-grel",
        "syllables": ["klo", "PID", "o", "grel"],
        "stress": [2],
        "category": "drug",
    },
    "furosemide": {
        "ipa": "/fjʊˈroʊsəmaɪd/",
        "simplified": "fyoo-ROH-se-mide",
        "syllables": ["fyoo", "ROH", "se", "mide"],
        "stress": [2],
        "category": "drug",
    },
    "insulin": {
        "ipa": "/ˈɪnsəlɪn/",
        "simplified": "IN-su-lin",
        "syllables": ["IN", "su", "lin"],
        "stress": [1],
        "category": "drug",
    },
    "ibuprofen": {
        "ipa": "/ˌaɪbjuːˈproʊfən/",
        "simplified": "eye-bew-PRO-fen",
        "syllables": ["eye", "bew", "PRO", "fen"],
        "stress": [3],
        "category": "drug",
    },
    "acetaminophen": {
        "ipa": "/əˌsiːtəˈmɪnəfən/",
        "simplified": "a-SEE-ta-MIN-o-fen",
        "syllables": ["a", "SEE", "ta", "MIN", "o", "fen"],
        "stress": [2, 4],
        "category": "drug",
    },
    "albuterol": {
        "ipa": "/ælˈbjuːtərɒl/",
        "simplified": "al-BYOO-ter-ol",
        "syllables": ["al", "BYOO", "ter", "ol"],
        "stress": [2],
        "category": "drug",
    },
    "sertraline": {
        "ipa": "/ˈsɜːrtrəliːn/",
        "simplified": "SUR-tra-leen",
        "syllables": ["SUR", "tra", "leen"],
        "stress": [1],
        "category": "drug",
    },
    "pantoprazole": {
        "ipa": "/pænˈtoʊprəzoʊl/",
        "simplified": "pan-TOH-pra-zole",
        "syllables": ["pan", "TOH", "pra", "zole"],
        "stress": [2],
        "category": "drug",
    },
    "amlodipine": {
        "ipa": "/æmˈloʊdɪpiːn/",
        "simplified": "am-LOH-di-peen",
        "syllables": ["am", "LOH", "di", "peen"],
        "stress": [2],
        "category": "drug",
    },
    "simvastatin": {
        "ipa": "/ˌsɪmvəˈstætɪn/",
        "simplified": "SIM-va-STA-tin",
        "syllables": ["SIM", "va", "STA", "tin"],
        "stress": [1, 3],
        "category": "drug",
    },
    "losartan": {
        "ipa": "/loʊˈsɑːrtæn/",
        "simplified": "lo-SAR-tan",
        "syllables": ["lo", "SAR", "tan"],
        "stress": [2],
        "category": "drug",
    },
    "rosuvastatin": {
        "ipa": "/roʊˌsuːvəˈstætɪn/",
        "simplified": "ro-SOO-va-STA-tin",
        "syllables": ["ro", "SOO", "va", "STA", "tin"],
        "stress": [2, 4],
        "category": "drug",
    },
    "ciprofloxacin": {
        "ipa": "/ˌsɪproʊˈflɒksəsɪn/",
        "simplified": "SIP-ro-FLOX-a-sin",
        "syllables": ["SIP", "ro", "FLOX", "a", "sin"],
        "stress": [1, 3],
        "category": "drug",
    },
    "tamsulosin": {
        "ipa": "/tæmˈsuːloʊsɪn/",
        "simplified": "tam-SOO-lo-sin",
        "syllables": ["tam", "SOO", "lo", "sin"],
        "stress": [2],
        "category": "drug",
    },
    "duloxetine": {
        "ipa": "/duːˈlɒksətiːn/",
        "simplified": "doo-LOX-e-teen",
        "syllables": ["doo", "LOX", "e", "teen"],
        "stress": [2],
        "category": "drug",
    },

    # ── Anatomy ──────────────────────────────────────────────────────────
    "pharynx": {
        "ipa": "/ˈfærɪŋks/",
        "simplified": "FAIR-inks",
        "syllables": ["FAIR", "inks"],
        "stress": [1],
        "category": "anatomy",
    },
    "larynx": {
        "ipa": "/ˈlærɪŋks/",
        "simplified": "LAIR-inks",
        "syllables": ["LAIR", "inks"],
        "stress": [1],
        "category": "anatomy",
    },
    "trachea": {
        "ipa": "/ˈtreɪkiə/",
        "simplified": "TRAY-kee-a",
        "syllables": ["TRAY", "kee", "a"],
        "stress": [1],
        "category": "anatomy",
    },
    "diaphragm": {
        "ipa": "/ˈdaɪəfræm/",
        "simplified": "DY-a-fram",
        "syllables": ["DY", "a", "fram"],
        "stress": [1],
        "category": "anatomy",
    },
    "femur": {
        "ipa": "/ˈfiːmər/",
        "simplified": "FEE-mur",
        "syllables": ["FEE", "mur"],
        "stress": [1],
        "category": "anatomy",
    },
    "patella": {
        "ipa": "/pəˈtɛlə/",
        "simplified": "pa-TEL-la",
        "syllables": ["pa", "TEL", "la"],
        "stress": [2],
        "category": "anatomy",
    },
    "clavicle": {
        "ipa": "/ˈklævɪkəl/",
        "simplified": "KLAV-i-kul",
        "syllables": ["KLAV", "i", "kul"],
        "stress": [1],
        "category": "anatomy",
    },
    "esophagus": {
        "ipa": "/ɪˈsɒfəɡəs/",
        "simplified": "ee-SOF-a-gus",
        "syllables": ["ee", "SOF", "a", "gus"],
        "stress": [2],
        "category": "anatomy",
    },
    "duodenum": {
        "ipa": "/ˌduːoʊˈdiːnəm/",
        "simplified": "doo-o-DEE-num",
        "syllables": ["doo", "o", "DEE", "num"],
        "stress": [3],
        "category": "anatomy",
    },
    "peritoneum": {
        "ipa": "/ˌpɛrɪtoʊˈniːəm/",
        "simplified": "PER-i-to-NEE-um",
        "syllables": ["PER", "i", "to", "NEE", "um"],
        "stress": [1, 4],
        "category": "anatomy",
    },
    "scapula": {
        "ipa": "/ˈskæpjʊlə/",
        "simplified": "SKAP-yu-la",
        "syllables": ["SKAP", "yu", "la"],
        "stress": [1],
        "category": "anatomy",
    },
    "sternum": {
        "ipa": "/ˈstɜːrnəm/",
        "simplified": "STUR-num",
        "syllables": ["STUR", "num"],
        "stress": [1],
        "category": "anatomy",
    },
    "vertebra": {
        "ipa": "/ˈvɜːrtɪbrə/",
        "simplified": "VUR-te-bra",
        "syllables": ["VUR", "te", "bra"],
        "stress": [1],
        "category": "anatomy",
    },
    "cerebellum": {
        "ipa": "/ˌsɛrəˈbɛləm/",
        "simplified": "SER-e-BEL-um",
        "syllables": ["SER", "e", "BEL", "um"],
        "stress": [1, 3],
        "category": "anatomy",
    },
    "myocardium": {
        "ipa": "/ˌmaɪoʊˈkɑːrdiəm/",
        "simplified": "MY-o-KAR-dee-um",
        "syllables": ["MY", "o", "KAR", "dee", "um"],
        "stress": [1, 3],
        "category": "anatomy",
    },

    # ── Conditions ───────────────────────────────────────────────────────
    "myocardial": {
        "ipa": "/ˌmaɪoʊˈkɑːrdiəl/",
        "simplified": "MY-o-KAR-dee-al",
        "syllables": ["MY", "o", "KAR", "dee", "al"],
        "stress": [1, 3],
        "category": "condition",
    },
    "pneumonia": {
        "ipa": "/njuːˈmoʊniə/",
        "simplified": "noo-MOH-nee-a",
        "syllables": ["noo", "MOH", "nee", "a"],
        "stress": [2],
        "category": "condition",
    },
    "hypertension": {
        "ipa": "/ˌhaɪpərˈtɛnʃən/",
        "simplified": "HY-per-TEN-shun",
        "syllables": ["HY", "per", "TEN", "shun"],
        "stress": [1, 3],
        "category": "condition",
    },
    "hyperlipidemia": {
        "ipa": "/ˌhaɪpərˌlɪpɪˈdiːmiə/",
        "simplified": "HY-per-LIP-i-DEE-mee-a",
        "syllables": ["HY", "per", "LIP", "i", "DEE", "mee", "a"],
        "stress": [1, 3, 5],
        "category": "condition",
    },
    "osteoporosis": {
        "ipa": "/ˌɒstioʊpəˈroʊsɪs/",
        "simplified": "OS-tee-o-po-ROH-sis",
        "syllables": ["OS", "tee", "o", "po", "ROH", "sis"],
        "stress": [1, 5],
        "category": "condition",
    },
    "psoriasis": {
        "ipa": "/səˈraɪəsɪs/",
        "simplified": "so-RY-a-sis",
        "syllables": ["so", "RY", "a", "sis"],
        "stress": [2],
        "category": "condition",
    },
    "fibromyalgia": {
        "ipa": "/ˌfaɪbroʊmaɪˈældʒə/",
        "simplified": "FY-bro-my-AL-ja",
        "syllables": ["FY", "bro", "my", "AL", "ja"],
        "stress": [1, 4],
        "category": "condition",
    },
    "tachycardia": {
        "ipa": "/ˌtækɪˈkɑːrdiə/",
        "simplified": "TAK-i-KAR-dee-a",
        "syllables": ["TAK", "i", "KAR", "dee", "a"],
        "stress": [1, 3],
        "category": "condition",
    },
    "bradycardia": {
        "ipa": "/ˌbrædɪˈkɑːrdiə/",
        "simplified": "BRAD-i-KAR-dee-a",
        "syllables": ["BRAD", "i", "KAR", "dee", "a"],
        "stress": [1, 3],
        "category": "condition",
    },
    "arrhythmia": {
        "ipa": "/əˈrɪðmiə/",
        "simplified": "a-RITH-mee-a",
        "syllables": ["a", "RITH", "mee", "a"],
        "stress": [2],
        "category": "condition",
    },
    "ischemia": {
        "ipa": "/ɪˈskiːmiə/",
        "simplified": "is-KEE-mee-a",
        "syllables": ["is", "KEE", "mee", "a"],
        "stress": [2],
        "category": "condition",
    },
    "sepsis": {
        "ipa": "/ˈsɛpsɪs/",
        "simplified": "SEP-sis",
        "syllables": ["SEP", "sis"],
        "stress": [1],
        "category": "condition",
    },
    "embolism": {
        "ipa": "/ˈɛmbəlɪzəm/",
        "simplified": "EM-bo-li-zum",
        "syllables": ["EM", "bo", "li", "zum"],
        "stress": [1],
        "category": "condition",
    },
    "edema": {
        "ipa": "/ɪˈdiːmə/",
        "simplified": "e-DEE-ma",
        "syllables": ["e", "DEE", "ma"],
        "stress": [2],
        "category": "condition",
    },
    "anemia": {
        "ipa": "/əˈniːmiə/",
        "simplified": "a-NEE-mee-a",
        "syllables": ["a", "NEE", "mee", "a"],
        "stress": [2],
        "category": "condition",
    },
    "diabetes": {
        "ipa": "/ˌdaɪəˈbiːtiːz/",
        "simplified": "DY-a-BEE-teez",
        "syllables": ["DY", "a", "BEE", "teez"],
        "stress": [1, 3],
        "category": "condition",
    },
    "asthma": {
        "ipa": "/ˈæzmə/",
        "simplified": "AZ-ma",
        "syllables": ["AZ", "ma"],
        "stress": [1],
        "category": "condition",
    },
    "cirrhosis": {
        "ipa": "/sɪˈroʊsɪs/",
        "simplified": "si-ROH-sis",
        "syllables": ["si", "ROH", "sis"],
        "stress": [2],
        "category": "condition",
    },
    "nephropathy": {
        "ipa": "/nɪˈfrɒpəθi/",
        "simplified": "ne-FROP-a-thee",
        "syllables": ["ne", "FROP", "a", "thee"],
        "stress": [2],
        "category": "condition",
    },
    "neuropathy": {
        "ipa": "/njʊˈrɒpəθi/",
        "simplified": "noo-ROP-a-thee",
        "syllables": ["noo", "ROP", "a", "thee"],
        "stress": [2],
        "category": "condition",
    },
    "dyspnea": {
        "ipa": "/dɪspˈniːə/",
        "simplified": "disp-NEE-a",
        "syllables": ["disp", "NEE", "a"],
        "stress": [2],
        "category": "condition",
    },
    "hypoglycemia": {
        "ipa": "/ˌhaɪpoʊɡlaɪˈsiːmiə/",
        "simplified": "HY-po-gly-SEE-mee-a",
        "syllables": ["HY", "po", "gly", "SEE", "mee", "a"],
        "stress": [1, 4],
        "category": "condition",
    },
    "hyperglycemia": {
        "ipa": "/ˌhaɪpərɡlaɪˈsiːmiə/",
        "simplified": "HY-per-gly-SEE-mee-a",
        "syllables": ["HY", "per", "gly", "SEE", "mee", "a"],
        "stress": [1, 4],
        "category": "condition",
    },
    "metastasis": {
        "ipa": "/məˈtæstəsɪs/",
        "simplified": "me-TAS-ta-sis",
        "syllables": ["me", "TAS", "ta", "sis"],
        "stress": [2],
        "category": "condition",
    },

    # ── Procedures ───────────────────────────────────────────────────────
    "auscultation": {
        "ipa": "/ˌɔːskəlˈteɪʃən/",
        "simplified": "AWS-kul-TAY-shun",
        "syllables": ["AWS", "kul", "TAY", "shun"],
        "stress": [1, 3],
        "category": "procedure",
    },
    "intubation": {
        "ipa": "/ˌɪntjuːˈbeɪʃən/",
        "simplified": "IN-too-BAY-shun",
        "syllables": ["IN", "too", "BAY", "shun"],
        "stress": [1, 3],
        "category": "procedure",
    },
    "catheterization": {
        "ipa": "/ˌkæθɪtəraɪˈzeɪʃən/",
        "simplified": "KATH-e-ter-i-ZAY-shun",
        "syllables": ["KATH", "e", "ter", "i", "ZAY", "shun"],
        "stress": [1, 5],
        "category": "procedure",
    },
    "echocardiogram": {
        "ipa": "/ˌɛkoʊˈkɑːrdioʊɡræm/",
        "simplified": "EK-o-KAR-dee-o-gram",
        "syllables": ["EK", "o", "KAR", "dee", "o", "gram"],
        "stress": [1, 3],
        "category": "procedure",
    },
    "angioplasty": {
        "ipa": "/ˈændʒioʊplæsti/",
        "simplified": "AN-jee-o-plas-tee",
        "syllables": ["AN", "jee", "o", "plas", "tee"],
        "stress": [1],
        "category": "procedure",
    },
    "endoscopy": {
        "ipa": "/ɛnˈdɒskəpi/",
        "simplified": "en-DOS-ko-pee",
        "syllables": ["en", "DOS", "ko", "pee"],
        "stress": [2],
        "category": "procedure",
    },
    "biopsy": {
        "ipa": "/ˈbaɪɒpsi/",
        "simplified": "BY-op-see",
        "syllables": ["BY", "op", "see"],
        "stress": [1],
        "category": "procedure",
    },
    "anesthesia": {
        "ipa": "/ˌænəsˈθiːʒə/",
        "simplified": "AN-es-THEE-zha",
        "syllables": ["AN", "es", "THEE", "zha"],
        "stress": [1, 3],
        "category": "procedure",
    },
}


# Chemical / drug suffixes that strongly signal a pharmaceutical name.
# Used by the OOV detector and by detectors that want to widen coverage.
DRUG_SUFFIXES = (
    "statin", "mab", "pril", "olol", "zole", "sartan", "cillin",
    "mycin", "floxacin", "dipine", "azepam", "azine", "tinib", "vir",
    "prazole", "parin", "caine",
)


def all_terms():
    """Return the sorted list of dictionary keys (all lowercase)."""
    return sorted(MEDICAL_DICT.keys())


def count_by_category():
    counts = {}
    for entry in MEDICAL_DICT.values():
        counts[entry["category"]] = counts.get(entry["category"], 0) + 1
    return counts


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(f"Total terms: {len(MEDICAL_DICT)}")
    print(f"By category: {count_by_category()}")
    # spot-check a few entries are well-formed
    for key in ("atorvastatin", "pharynx", "myocardial"):
        e = MEDICAL_DICT[key]
        assert e["syllables"], key
        assert all(1 <= s <= len(e["syllables"]) for s in e["stress"]), key
        print(f"  {key:16s} {e['ipa']:30s} {e['simplified']}")
    print("medical_dictionary self-check OK")
