import pytest
from unittest.mock import patch, MagicMock


def test_transcribe_no_audio(client):
    res = client.post("/api/transcribe", data=b"", content_type="audio/wav")
    assert res.status_code == 400


def test_transcribe_oversized(client):
    big = b"x" * (11 * 1024 * 1024)
    res = client.post("/api/transcribe", data=big, content_type="audio/wav")
    assert res.status_code == 413


def test_transcription_service_returns_dict():
    from app.services.transcription import TranscriptionService

    mock_segment = MagicMock()
    mock_segment.start = 0.0
    mock_segment.end = 1.5
    mock_segment.text = " Hello world"

    mock_info = MagicMock()
    mock_info.language = "en"
    mock_info.language_probability = 0.99

    service = TranscriptionService(model_size="tiny")

    with patch.object(service, "_get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        mock_get_model.return_value = mock_model

        import tempfile, os
        with patch("tempfile.NamedTemporaryFile") as mock_tmp:
            mock_file = MagicMock()
            mock_file.__enter__ = lambda s: s
            mock_file.__exit__ = MagicMock(return_value=False)
            mock_file.name = "fake.wav"
            mock_tmp.return_value = mock_file

            with patch("os.unlink"):
                result = service.transcribe(b"fake-audio")

    assert result["language"] == "en"
    assert result["confidence"] == 0.99
    assert "text" in result
    assert "segments" in result
