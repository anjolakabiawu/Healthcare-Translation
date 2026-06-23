"""
Feature 5 — Out-of-Vocabulary (OOV) detection and logging.

Flags words the ASR model likely struggles with (outside its training
distribution), combining three signals:

  1. Low confidence from Whisper  (below OOV_CONFIDENCE = 0.70)
  2. The word isn't a common English word (bundled wordlist; NLTK `words`
     corpus is used to enrich the list when available, else we fall back to
     the bundled set so the detector never hard-fails)
  3. The word matches OOV-prone patterns: long compounds, drug suffixes
     (-statin, -mab, -pril, -olol, -zole, ...), or non-dictionary brand/
     foreign-looking tokens

A word is flagged OOV when it triggers at least two of the three signals
(or the drug-suffix signal alone, which is a strong pharmaceutical cue).

Detected terms are appended to an in-memory session log; `get_log()` and
`get_stats()` expose them for the sidebar panel.
"""

from __future__ import annotations

import re
import sys
import os
from datetime import datetime, timezone

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from data.medical_dictionary import MEDICAL_DICT, DRUG_SUFFIXES  # noqa: E402

OOV_CONFIDENCE = 0.70
LONG_WORD_LEN = 12      # words this long are compound/technical-prone

# A compact set of common English words. Not exhaustive — it's a fast
# first-pass filter; the goal is "is this an everyday word?", not a dictionary.
_COMMON_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "so", "to", "of", "in",
    "on", "at", "by", "for", "with", "from", "into", "over", "under", "again",
    "is", "are", "was", "were", "be", "been", "being", "am", "has", "have",
    "had", "do", "does", "did", "will", "would", "can", "could", "should",
    "may", "might", "must", "shall", "this", "that", "these", "those", "it",
    "he", "she", "they", "we", "you", "i", "him", "her", "them", "his", "their",
    "patient", "patients", "doctor", "nurse", "hospital", "clinic", "pain",
    "left", "right", "today", "yesterday", "tomorrow", "morning", "night",
    "took", "take", "taking", "started", "stopped", "feeling", "feels", "felt",
    "has", "showed", "shows", "complains", "reports", "history", "blood",
    "pressure", "heart", "rate", "test", "tests", "result", "results", "scan",
    "x-ray", "fever", "cough", "cold", "flu", "headache", "stomach", "chest",
    "back", "leg", "arm", "head", "eye", "ear", "throat", "skin", "bone",
    "two", "three", "four", "five", "ten", "days", "weeks", "months", "years",
    "high", "low", "normal", "severe", "mild", "acute", "chronic", "after",
    "before", "during", "since", "weeks", "week", "day", "hour", "hours",
    "treatment", "medicine", "tablet", "tablets", "dose", "twice", "daily",
}


class OOVDetector:
    def __init__(self):
        self._log: list[dict] = []
        self._words = self._build_wordlist()
        # lowercase set of known medical dictionary terms (these are NOT OOV —
        # they're known, just specialized)
        self._medical = set(MEDICAL_DICT.keys())

    @staticmethod
    def _build_wordlist() -> set[str]:
        words = set(_COMMON_WORDS)
        try:  # enrich with NLTK if the corpus happens to be present
            import nltk
            try:
                from nltk.corpus import words as nltk_words
                words |= {w.lower() for w in nltk_words.words()}
            except LookupError:
                # corpus not present yet — download it once, then load
                nltk.download("words", quiet=True)
                from nltk.corpus import words as nltk_words
                words |= {w.lower() for w in nltk_words.words()}
        except Exception:
            pass  # bundled set is enough as a fallback
        return words

    @staticmethod
    def _normalize(word: str) -> str:
        return re.sub(r"[^a-z]", "", word.lower())

    def _matches_pattern(self, word: str) -> bool:
        norm = self._normalize(word)
        if not norm:
            return False
        if any(norm.endswith(suf) for suf in DRUG_SUFFIXES):
            return True
        if len(norm) >= LONG_WORD_LEN:
            return True
        return False

    def _known_word(self, norm: str) -> bool:
        """Is this a known word? Tries the word as-is, then common inflections
        (drugs→drug, recommended→recommend) since the wordlist stores base forms."""
        if norm in self._words or norm in self._medical:
            return True
        for suf in ("s", "es", "ed", "d", "ing", "ly", "er"):
            if norm.endswith(suf):
                stem = norm[: -len(suf)]
                if len(stem) >= 3 and (stem in self._words or stem in self._medical):
                    return True
        # handle doubled-consonant + ing/ed (e.g. "stopped" -> "stop")
        if len(norm) > 4 and norm[-3] == norm[-4] and norm[:-4] in self._words:
            return True
        return False

    def detect_word(self, word: str, confidence: float = 1.0) -> dict | None:
        """Return an OOV record if `word` is flagged, else None."""
        norm = self._normalize(word)
        if not norm or len(norm) < 3:
            return None

        signals = []
        low_conf = confidence < OOV_CONFIDENCE
        not_common = not self._known_word(norm)
        suffix_hit = any(norm.endswith(suf) for suf in DRUG_SUFFIXES)
        pattern_hit = self._matches_pattern(word)

        if low_conf:
            signals.append("low_confidence")
        if not_common:
            signals.append("not_in_wordlist")
        if pattern_hit:
            signals.append("pattern_match")

        # Flag when:
        #   - >=2 signals fire, OR
        #   - the strong drug-suffix cue alone, OR
        #   - a reasonably long word (>=5 chars) isn't a known word at all.
        #     Real words rarely fail the wordlist; a long unknown token is most
        #     often a misheard term ("malera") or a name/brand worth reviewing.
        long_nonword = not_common and len(norm) >= 5
        flagged = len(signals) >= 2 or suffix_hit or long_nonword
        if not flagged:
            return None

        category = "drug_name" if suffix_hit else (
            "compound" if (pattern_hit and len(norm) >= LONG_WORD_LEN) else "unknown")

        return {
            "term": word,
            "confidence": round(float(confidence), 3),
            "signals": signals,
            "category": category,
        }

    def analyze(self, words: list[dict], context: str = "") -> list[dict]:
        """Scan a word list (from transcription), log + return OOV hits."""
        hits = []
        ts = datetime.now(timezone.utc).isoformat()
        for w in words:
            rec = self.detect_word(w.get("word", ""), w.get("probability", 1.0))
            if rec:
                rec["context"] = context
                rec["timestamp"] = ts
                self._log.append(rec)
                hits.append(rec)
        return hits

    def get_log(self) -> list[dict]:
        return list(self._log)

    def get_stats(self) -> dict:
        counts = {}
        for rec in self._log:
            counts[rec["category"]] = counts.get(rec["category"], 0) + 1
        return {"total": len(self._log), "by_category": counts}

    def clear(self):
        self._log.clear()


# module-level singleton
oov_detector = OOVDetector()


if __name__ == "__main__":
    d = OOVDetector()

    # Test 1: a drug-suffix word is flagged via the suffix cue alone
    r1 = d.detect_word("rosuvastatin", 0.95)
    print("1.", r1)
    assert r1 and "pattern_match" in r1["signals"] and r1["category"] == "drug_name"

    # Test 2: a common word at high confidence is NOT flagged
    r2 = d.detect_word("patient", 0.99)
    print("2.", r2)
    assert r2 is None

    # Test 3: a made-up low-confidence non-word trips >=2 signals
    r3 = d.detect_word("zibblefrump", 0.40)
    print("3.", r3)
    assert r3 and "low_confidence" in r3["signals"] and "not_in_wordlist" in r3["signals"]

    # Test 4: analyze() logs hits and stats reflect them
    d.clear()
    hits = d.analyze([
        {"word": "Patient", "probability": 0.99},
        {"word": "metoprolol", "probability": 0.96},   # -olol suffix
        {"word": "blarghicillin", "probability": 0.55}, # -cillin + low conf + nonword
    ], context="patient on metoprolol")
    stats = d.get_stats()
    print("4. hits", [h["term"] for h in hits], "stats", stats)
    assert len(hits) == 2
    assert stats["total"] == 2 and stats["by_category"].get("drug_name", 0) >= 1

    print("oov_detector self-check OK")
