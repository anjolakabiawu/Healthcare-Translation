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
            # word_timestamps=True makes faster-whisper attach per-word
            # probabilities, which Feature 3 (confidence scoring) consumes.
            segments, info = model.transcribe(tmp_path, beam_size=5, word_timestamps=True)
            segment_list = []
            full_text_parts = []
            words = []

            for seg in segments:
                segment_list.append({
                    "start": round(seg.start, 2),
                    "end": round(seg.end, 2),
                    "text": seg.text.strip(),
                })
                full_text_parts.append(seg.text.strip())
                for w in (seg.words or []):
                    words.append({
                        "word": w.word.strip(),
                        "start": round(w.start, 2),
                        "end": round(w.end, 2),
                        "probability": round(w.probability, 3),
                    })

            return {
                "text": " ".join(full_text_parts),
                "language": info.language,
                "confidence": round(info.language_probability, 3),
                "segments": segment_list,
                "words": words,
            }
        finally:
            os.unlink(tmp_path)


transcription_service = TranscriptionService()
