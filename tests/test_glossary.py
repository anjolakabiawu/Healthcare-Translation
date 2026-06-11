import pytest
from app.services.glossary import GlossaryService
import os
import tempfile


SAMPLE_CSV = """source_term,target_term,source_lang,target_lang
Hypertension,Hipertensión,EN,ES
Fever,Fiebre,EN,ES
Blood Pressure,Tension artérielle,EN,FR
"""


@pytest.fixture
def glossary(tmp_path):
    csv_file = tmp_path / "glossary.csv"
    csv_file.write_text(SAMPLE_CSV, encoding="utf-8")
    return GlossaryService(str(csv_file))


def test_highlight_wraps_known_term(glossary):
    result = glossary.highlight_terms("Patient has Hypertension.", "EN", "ES")
    assert "<mark class='medical-term'>Hypertension</mark>" in result


def test_highlight_case_insensitive(glossary):
    result = glossary.highlight_terms("Patient has fever.", "EN", "ES")
    assert "<mark class='medical-term'>" in result


def test_highlight_unknown_term_unchanged(glossary):
    result = glossary.highlight_terms("Patient has a cold.", "EN", "ES")
    assert result == "Patient has a cold."


def test_apply_glossary_replaces_term(glossary):
    result = glossary.apply_glossary("Patient has Hypertension.", "EN", "ES")
    assert "Hipertensión" in result


def test_apply_glossary_wrong_pair_no_change(glossary):
    result = glossary.apply_glossary("Patient has Fever.", "EN", "DE")
    assert "Fiebre" not in result


def test_highlight_translated_terms(glossary):
    result = glossary.highlight_translated_terms("Il a de la Tension artérielle élevée.", "EN", "FR")
    assert "<mark class='medical-term'>" in result
