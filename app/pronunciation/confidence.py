"""
Feature 3 — ASR confidence scoring per word.

faster-whisper returns a per-word probability when transcribing with
`word_timestamps=True`. `ConfidenceAnalyzer` turns that raw output into a
flagged word list the UI can highlight:

  - any word below LOW_CONFIDENCE (0.75) is flagged "uncertain"
  - any *medical* word (in MEDICAL_DICT) below MEDICAL_CONFIDENCE (0.85) is
    flagged "high-risk" — medical accuracy matters more, so the bar is higher

Output per word:
    {word, confidence, is_medical, flagged, flag_reason}

Plus an overall confidence score for the whole transcript.
"""

from __future__ import annotations

import re
import sys
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from data.medical_dictionary import MEDICAL_DICT  # noqa: E402

# Below this, any word is "uncertain". Kept fairly low so ordinary words that
# a decent model scores in the 0.6–0.8 range don't all light up; the point is
# to surface the genuinely shaky words, not most of the sentence.
LOW_CONFIDENCE = 0.55
MEDICAL_CONFIDENCE = 0.85   # below this, a medical word is "high-risk"

# Build a lowercase set of dictionary terms once for fast membership tests.
_MEDICAL_TERMS = set(MEDICAL_DICT.keys())


def _normalize(word: str) -> str:
    """Strip punctuation/whitespace and lowercase for dictionary matching."""
    return re.sub(r"[^a-z]", "", word.lower())


class ConfidenceAnalyzer:
    def __init__(self, low=LOW_CONFIDENCE, medical=MEDICAL_CONFIDENCE):
        self.low = low
        self.medical = medical

    def is_medical(self, word: str) -> bool:
        norm = _normalize(word)
        if not norm:
            return False
        # exact, or singular form of a simple plural
        if norm in _MEDICAL_TERMS:
            return True
        if norm.endswith("s") and norm[:-1] in _MEDICAL_TERMS:
            return True
        if norm.endswith("es") and norm[:-2] in _MEDICAL_TERMS:
            return True
        return False

    def analyze_word(self, word: str, confidence: float) -> dict:
        conf = round(float(confidence), 3)
        medical = self.is_medical(word)
        flagged = False
        reason = None

        if medical and conf < self.medical:
            flagged = True
            reason = "high-risk"          # medical term below the higher bar
        elif conf < self.low:
            flagged = True
            reason = "uncertain"

        return {
            "word": word,
            "confidence": conf,
            "is_medical": medical,
            "flagged": flagged,
            "flag_reason": reason,
        }

    def analyze(self, words: list[dict]) -> dict:
        """
        `words` is a list of {"word": str, "probability": float} dicts
        (as produced by the transcription service from faster-whisper).
        Returns the per-word analysis plus aggregate stats.
        """
        analyzed = [self.analyze_word(w.get("word", ""), w.get("probability", 1.0))
                    for w in words]

        confs = [w["confidence"] for w in analyzed]
        overall = round(sum(confs) / len(confs), 3) if confs else 0.0
        flagged_count = sum(1 for w in analyzed if w["flagged"])
        high_risk = sum(1 for w in analyzed if w["flag_reason"] == "high-risk")

        return {
            "words": analyzed,
            "overall_confidence": overall,
            "flagged_count": flagged_count,
            "high_risk_count": high_risk,
            "word_count": len(analyzed),
        }


# module-level singleton
confidence_analyzer = ConfidenceAnalyzer()


if __name__ == "__main__":
    a = ConfidenceAnalyzer()

    # Test 1: a low-confidence ordinary word is flagged "uncertain"
    r1 = a.analyze_word("the", 0.40)
    print("1.", r1)
    assert r1["flagged"] and r1["flag_reason"] == "uncertain"
    assert not r1["is_medical"]

    # Test 2: a medical word between the two thresholds is "high-risk"
    # (0.80 is above the 0.75 generic bar but below the 0.85 medical bar)
    r2 = a.analyze_word("Malaria", 0.80)
    print("2.", r2)
    assert r2["is_medical"]
    assert r2["flagged"] and r2["flag_reason"] == "high-risk"

    # Test 3: high-confidence words are not flagged; plurals detected medical
    r3 = a.analyze_word("Conditions", 0.95)
    print("3.", r3)
    assert not r3["flagged"]         # high confidence -> no flag
    r3b = a.analyze_word("anesthesia", 0.95)
    assert r3b["is_medical"] and not r3b["flagged"]   # known term, confident

    # Test 4: aggregate stats over a mixed list
    agg = a.analyze([
        {"word": "Patient", "probability": 0.99},
        {"word": "has", "probability": 0.98},
        {"word": "malaria", "probability": 0.70},   # high-risk medical
        {"word": "umm", "probability": 0.50},        # uncertain
    ])
    print("4.", "overall", agg["overall_confidence"],
          "flagged", agg["flagged_count"], "high_risk", agg["high_risk_count"])
    assert agg["word_count"] == 4
    assert agg["flagged_count"] == 2
    assert agg["high_risk_count"] == 1

    print("confidence self-check OK")
