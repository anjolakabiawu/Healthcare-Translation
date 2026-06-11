import tempfile
import os
from faster_whisper import WhisperModel


class TranscriptionService:
    def __init__(self, model_size: str = "base"):
        self._model = None
        self.model_size = model_size

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        return self._model

    def transcribe(self, audio_bytes: bytes) -> dict:
        model = self._get_model()

        # ffmpeg (used by faster-whisper) decodes by content, not extension,
        # so this handles WAV, WebM/Opus (MediaRecorder), OGG, etc.
        with tempfile.NamedTemporaryFile(suffix=".audio", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            segments, info = model.transcribe(tmp_path, beam_size=5)
            segment_list = []
            full_text_parts = []

            for seg in segments:
                segment_list.append({
                    "start": round(seg.start, 2),
                    "end": round(seg.end, 2),
                    "text": seg.text.strip(),
                })
                full_text_parts.append(seg.text.strip())

            return {
                "text": " ".join(full_text_parts),
                "language": info.language,
                "confidence": round(info.language_probability, 3),
                "segments": segment_list,
            }
        finally:
            os.unlink(tmp_path)


transcription_service = TranscriptionService()
