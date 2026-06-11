import pytest
from unittest.mock import patch, MagicMock
from app.services.translation import TranslationService


@pytest.fixture
def service():
    return TranslationService()


def test_unsupported_pair_raises(service):
    with pytest.raises(ValueError, match="Unsupported"):
        service.translate("hello", "en", "xx")


def test_supported_pairs_list():
    pairs = TranslationService.supported_pairs()
    assert isinstance(pairs, list)
    assert len(pairs) > 0
    assert all("source" in p and "target" in p for p in pairs)


def test_en_es_in_supported_pairs():
    pairs = TranslationService.supported_pairs()
    sources_targets = [(p["source"], p["target"]) for p in pairs]
    assert ("en", "es") in sources_targets


def test_translate_calls_mymemory(service):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "responseStatus": 200,
        "responseData": {"translatedText": "Hola mundo"},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("app.services.translation.requests.get", return_value=mock_response):
        result = service.translate("Hello world", "en", "es")

    assert result["translated_text"] == "Hola mundo"
    assert result["source_lang"] == "en"
    assert result["target_lang"] == "es"


def test_translate_quota_exceeded_raises(service):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "responseStatus": 200,
        "responseData": {"translatedText": "HELLO WORLD"},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("app.services.translation.requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="quota"):
            service.translate("Hello world", "en", "es")
