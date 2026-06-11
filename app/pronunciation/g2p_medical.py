"""
Feature 1 — Medical-term grapheme-to-phoneme (G2P) layer.

`MedicalG2P` resolves a written term to a phonetic representation:

  1. First it consults the curated MEDICAL_DICT (data/medical_dictionary.py).
     This is authoritative — standard G2P gets most medical terms wrong.
  2. If the term is unknown, it falls back to the `g2p-en` engine (ARPAbet),
     converted to a rough IPA + simplified guide.
  3. If g2p-en is unavailable (not installed, or NLTK data missing), it falls
     back to a lightweight heuristic syllabifier so the function never raises.

`get_pronunciation(term)` returns a dict:
    {
      "term":        original input,
      "ipa":         IPA string (slashes included when from the dictionary),
      "simplified":  readable guide, stressed syllables in CAPS,
      "syllables":   list[str],
      "stress":      list[int]  (1-based indices into `syllables`),
      "source":      "dictionary" | "g2p-en" | "heuristic",
      "confidence":  float 0..1
    }
"""

from __future__ import annotations

import re
import sys
import os

# Make the project-root `data` package importable whether this module is run
# directly or imported via the app package.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from data.medical_dictionary import MEDICAL_DICT  # noqa: E402


# ── ARPAbet → IPA (vowels carry stress digits 0/1/2 we strip first) ───────
_ARPABET_TO_IPA = {
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ",
    "B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "EH": "ɛ", "ER": "ɜr",
    "EY": "eɪ", "F": "f", "G": "ɡ", "HH": "h", "IH": "ɪ", "IY": "iː",
    "JH": "dʒ", "K": "k", "L": "l", "M": "m", "N": "n", "NG": "ŋ",
    "OW": "oʊ", "OY": "ɔɪ", "P": "p", "R": "r", "S": "s", "SH": "ʃ",
    "T": "t", "TH": "θ", "UH": "ʊ", "UW": "uː", "V": "v", "W": "w",
    "Y": "j", "Z": "z", "ZH": "ʒ",
}

# Rough ARPAbet → readable spelling for the simplified guide.
_ARPABET_TO_READABLE = {
    "AA": "ah", "AE": "a", "AH": "uh", "AO": "aw", "AW": "ow", "AY": "y",
    "B": "b", "CH": "ch", "D": "d", "DH": "th", "EH": "eh", "ER": "ur",
    "EY": "ay", "F": "f", "G": "g", "HH": "h", "IH": "ih", "IY": "ee",
    "JH": "j", "K": "k", "L": "l", "M": "m", "N": "n", "NG": "ng",
    "OW": "oh", "OY": "oy", "P": "p", "R": "r", "S": "s", "SH": "sh",
    "T": "t", "TH": "th", "UH": "oo", "UW": "oo", "V": "v", "W": "w",
    "Y": "y", "Z": "z", "ZH": "zh",
}

_VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY",
           "IH", "IY", "OW", "OY", "UH", "UW"}


class MedicalG2P:
    def __init__(self):
        self._g2p = None
        self._g2p_tried = False

    # ── lazy g2p-en loader (optional dependency) ─────────────────────────
    def _get_g2p(self):
        if self._g2p_tried:
            return self._g2p
        self._g2p_tried = True
        try:
            from g2p_en import G2p  # type: ignore
            self._g2p = G2p()
        except Exception:
            self._g2p = None
        return self._g2p

    # ── public API ───────────────────────────────────────────────────────
    def get_pronunciation(self, term: str) -> dict:
        if not term or not term.strip():
            return self._empty(term)

        key = term.strip().lower()

        # 1. dictionary (authoritative)
        if key in MEDICAL_DICT:
            e = MEDICAL_DICT[key]
            return {
                "term": term,
                "ipa": e["ipa"],
                "simplified": e["simplified"],
                "syllables": list(e["syllables"]),
                "stress": list(e["stress"]),
                "source": "dictionary",
                "confidence": 1.0,
            }

        # 2. g2p-en fallback
        result = self._g2p_en(key)
        if result:
            return {"term": term, **result, "source": "g2p-en", "confidence": 0.6}

        # 3. heuristic fallback
        return {"term": term, **self._heuristic(key), "source": "heuristic",
                "confidence": 0.3}

    # ── g2p-en path ──────────────────────────────────────────────────────
    def _g2p_en(self, word: str) -> dict | None:
        g2p = self._get_g2p()
        if g2p is None:
            return None
        try:
            phones = g2p(word)
        except Exception:
            return None
        phones = [p for p in phones if re.match(r"^[A-Z]", p)]
        if not phones:
            return None

        ipa_parts, readable_parts = [], []
        stress_phone_idx = []  # indices of vowels carrying primary stress
        vowel_count = 0
        for p in phones:
            base = re.sub(r"\d", "", p)
            digit_match = re.search(r"(\d)", p)
            if base in _VOWELS:
                vowel_count += 1
                if digit_match and digit_match.group(1) == "1":
                    stress_phone_idx.append(vowel_count)
            ipa_parts.append(_ARPABET_TO_IPA.get(base, base.lower()))
            readable_parts.append(_ARPABET_TO_READABLE.get(base, base.lower()))

        ipa = "/" + "".join(ipa_parts) + "/"
        syllables = self._readable_to_syllables(readable_parts, phones)
        stress = stress_phone_idx or ([1] if syllables else [])
        simplified = self._format_simplified(syllables, stress)
        return {"ipa": ipa, "simplified": simplified,
                "syllables": syllables, "stress": stress}

    @staticmethod
    def _readable_to_syllables(readable_parts: list[str], phones: list[str]) -> list[str]:
        """Group phoneme spellings into rough syllables (one per vowel)."""
        syllables, current = [], ""
        for r, p in zip(readable_parts, phones):
            base = re.sub(r"\d", "", p)
            current += r
            if base in _VOWELS:
                syllables.append(current)
                current = ""
        if current:
            if syllables:
                syllables[-1] += current
            else:
                syllables.append(current)
        return syllables

    # ── heuristic path (no deps) ─────────────────────────────────────────
    def _heuristic(self, word: str) -> dict:
        syllables = self._syllabify(word)
        stress = [1] if syllables else []
        simplified = self._format_simplified(syllables, stress)
        return {
            "ipa": "/" + word + "/",   # best-effort: no real phonemes available
            "simplified": simplified,
            "syllables": syllables,
            "stress": stress,
        }

    @staticmethod
    def _syllabify(word: str) -> list[str]:
        """Very rough vowel-group syllabifier for unknown words."""
        groups = re.findall(r"[^aeiouy]*[aeiouy]+[^aeiouy]*", word, re.IGNORECASE)
        return groups or ([word] if word else [])

    # ── shared formatting ────────────────────────────────────────────────
    @staticmethod
    def _format_simplified(syllables: list[str], stress: list[int]) -> str:
        out = []
        for i, syl in enumerate(syllables, start=1):
            out.append(syl.upper() if i in stress else syl.lower())
        return "-".join(out)

    @staticmethod
    def _empty(term: str) -> dict:
        return {"term": term, "ipa": "", "simplified": "", "syllables": [],
                "stress": [], "source": "none", "confidence": 0.0}


# module-level singleton
medical_g2p = MedicalG2P()


def get_pronunciation(term: str) -> dict:
    """Convenience wrapper around the singleton."""
    return medical_g2p.get_pronunciation(term)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    g = MedicalG2P()

    # Test 1: dictionary hit is authoritative, confidence 1.0
    r1 = g.get_pronunciation("Atorvastatin")
    print("1.", r1["ipa"], r1["simplified"], r1["source"], r1["confidence"])
    assert r1["source"] == "dictionary"
    assert r1["confidence"] == 1.0
    assert r1["simplified"] == "ay-TOR-va-STA-tin"

    # Test 2: case-insensitive dictionary lookup
    r2 = g.get_pronunciation("PHARYNX")
    print("2.", r2["ipa"], r2["simplified"], r2["source"])
    assert r2["source"] == "dictionary"
    assert r2["syllables"] == ["FAIR", "inks"]

    # Test 3: unknown word falls back gracefully (g2p-en or heuristic),
    # never raises, always returns a simplified guide + syllables.
    r3 = g.get_pronunciation("bumblefloxidine")
    print("3.", r3["ipa"], r3["simplified"], r3["source"], r3["confidence"])
    assert r3["source"] in ("g2p-en", "heuristic")
    assert r3["syllables"]
    assert 0.0 < r3["confidence"] < 1.0

    # Test 4: empty input is handled
    r4 = g.get_pronunciation("")
    assert r4["source"] == "none" and r4["confidence"] == 0.0

    print("g2p_medical self-check OK")
