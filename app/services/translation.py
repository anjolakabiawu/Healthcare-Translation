import requests

SUPPORTED_PAIRS = {
    ("en", "es"), ("es", "en"),
    ("en", "fr"), ("fr", "en"),
    ("en", "de"), ("de", "en"),
    ("en", "zh"), ("zh", "en"),
    ("en", "pt"), ("pt", "en"),
    ("en", "ar"), ("ar", "en"),
    ("en", "ru"), ("ru", "en"),
    ("es", "fr"), ("fr", "es"),
    ("es", "de"), ("de", "es"),
}

LANGUAGE_NAMES = {
    "en": "English", "es": "Spanish", "fr": "French",
    "de": "German", "zh": "Chinese", "pt": "Portuguese",
    "ar": "Arabic", "ru": "Russian",
}

MYMEMORY_URL = "https://api.mymemory.translated.net/get"


class TranslationService:
    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        pair = (source_lang.lower(), target_lang.lower())
        if pair not in SUPPORTED_PAIRS:
            raise ValueError(f"Unsupported language pair: {source_lang} → {target_lang}")

        lang_pair = f"{source_lang.lower()}|{target_lang.lower()}"
        response = requests.get(
            MYMEMORY_URL,
            params={"q": text, "langpair": lang_pair},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("responseStatus") != 200:
            raise ValueError(data.get("responseDetails", "Translation failed"))

        translated = data["responseData"]["translatedText"]

        # MyMemory returns the original text in caps when it hits quota
        if translated.upper() == text.upper():
            raise ValueError("Translation quota exceeded or service unavailable. Try again shortly.")

        return {
            "translated_text": translated,
            "source_lang": source_lang,
            "target_lang": target_lang,
        }

    @staticmethod
    def supported_pairs() -> list:
        return [
            {"source": s, "target": t}
            for (s, t) in sorted(SUPPORTED_PAIRS)
        ]


translation_service = TranslationService()
