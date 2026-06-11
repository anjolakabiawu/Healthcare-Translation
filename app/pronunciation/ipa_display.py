"""
Feature 2 — IPA annotation of translated/transcribed text.

`MedicalTermDetector` scans text for known medical terms (case-insensitive,
tolerant of simple plurals/inflections) and returns, for each occurrence, its
position plus the full pronunciation payload from the G2P layer.

`annotate(text)` returns the original text wrapped so the frontend can render
detected terms with a hover tooltip:

    {
      "text": original text,
      "annotated_html": text with <span class="rx-term" data-...> wrappers,
      "terms": [ {term, start, end, ipa, simplified, syllables, stress}, ... ]
    }

Used by the /api/pronunciation/annotate endpoint and by the translate route to
enrich its highlighted output.
"""

from __future__ import annotations

import re
import sys
import os
import json
import html

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from data.medical_dictionary import MEDICAL_DICT  # noqa: E402
from app.pronunciation.g2p_medical import get_pronunciation  # noqa: E402


class MedicalTermDetector:
    def __init__(self):
        # Longest terms first so multi-word / longer matches win over shorter.
        self._terms = sorted(MEDICAL_DICT.keys(), key=len, reverse=True)
        # One regex that matches any dictionary term, allowing an optional
        # trailing inflection (s, es, 's) so plurals are caught.
        alternation = "|".join(re.escape(t) for t in self._terms)
        self._pattern = re.compile(
            r"(?<![A-Za-z])(" + alternation + r")(es|s|'s)?(?![A-Za-z])",
            re.IGNORECASE,
        )

    def detect(self, text: str) -> list[dict]:
        """Return a list of detected medical terms with positions + pronunciation."""
        if not text:
            return []
        found = []
        for m in self._pattern.finditer(text):
            base = m.group(1).lower()
            entry = MEDICAL_DICT.get(base)
            if not entry:
                continue
            pron = get_pronunciation(base)
            found.append({
                "term": m.group(0),       # as it appears (incl. plural suffix)
                "base": base,
                "start": m.start(),
                "end": m.end(),
                "ipa": pron["ipa"],
                "simplified": pron["simplified"],
                "syllables": pron["syllables"],
                "stress": pron["stress"],
                "category": entry["category"],
            })
        return found

    def annotate(self, text: str) -> dict:
        """Wrap detected terms in tooltip-ready spans and return structured data."""
        terms = self.detect(text)
        if not terms:
            return {"text": text, "annotated_html": html.escape(text), "terms": []}

        # Rebuild the string, escaping non-term chunks and wrapping terms.
        out = []
        cursor = 0
        for t in terms:
            out.append(html.escape(text[cursor:t["start"]]))
            label = html.escape(text[t["start"]:t["end"]])
            data = html.escape(json.dumps({
                "term": t["base"],
                "ipa": t["ipa"],
                "simplified": t["simplified"],
                "syllables": t["syllables"],
                "stress": t["stress"],
            }), quote=True)
            out.append(
                f'<span class="rx-term" data-pron="{data}" '
                f'tabindex="0" role="button" aria-label="Pronunciation of {label}">'
                f'{label}</span>'
            )
            cursor = t["end"]
        out.append(html.escape(text[cursor:]))

        return {"text": text, "annotated_html": "".join(out), "terms": terms}


# module-level singleton
term_detector = MedicalTermDetector()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    d = MedicalTermDetector()

    # Test 1: detects multiple terms with correct positions
    text1 = "Patient on atorvastatin with pharynx inflammation and hypertension."
    res1 = d.annotate(text1)
    names = [t["base"] for t in res1["terms"]]
    print("1.", names)
    assert "atorvastatin" in names
    assert "pharynx" in names
    assert "hypertension" in names
    # positions point at the right substring
    for t in res1["terms"]:
        assert text1[t["start"]:t["end"]].lower().startswith(t["base"][:4])

    # Test 2: plural / inflected forms are caught
    text2 = "Two patients showed arrhythmias on their echocardiograms."
    res2 = d.annotate(text2)
    bases2 = {t["base"] for t in res2["terms"]}
    print("2.", [t["term"] for t in res2["terms"]])
    assert "arrhythmia" in bases2
    assert "echocardiogram" in bases2

    # Test 3: annotated HTML wraps terms and escapes the rest
    assert 'class="rx-term"' in res1["annotated_html"]
    assert "data-pron" in res1["annotated_html"]
    # no raw term should leak unescaped angle brackets
    html3 = d.annotate("a < b and metformin")["annotated_html"]
    print("3.", html3)
    assert "&lt;" in html3
    assert "rx-term" in html3

    # Test 4: empty / no-match input
    assert d.annotate("")["terms"] == []
    assert d.annotate("the quick brown fox")["terms"] == []

    print("ipa_display self-check OK")
