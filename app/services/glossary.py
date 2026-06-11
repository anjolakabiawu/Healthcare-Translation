import re
import os
import pandas as pd


_GLOSSARY_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "glossary.csv")


class GlossaryService:
    def __init__(self, csv_path: str = _GLOSSARY_PATH):
        self._df = None
        self.csv_path = os.path.abspath(csv_path)
        self._load()

    def _load(self):
        try:
            self._df = pd.read_csv(self.csv_path)
            required = {"source_term", "target_term", "source_lang", "target_lang"}
            if not required.issubset(self._df.columns):
                self._df = None
        except FileNotFoundError:
            self._df = None

    def _get_pairs(self, source_lang: str, target_lang: str) -> list[tuple[str, str]]:
        if self._df is None:
            return []
        mask = (
            (self._df["source_lang"].str.upper() == source_lang.upper()) &
            (self._df["target_lang"].str.upper() == target_lang.upper())
        )
        rows = self._df[mask]
        return list(zip(rows["source_term"], rows["target_term"]))

    def apply_glossary(self, text: str, source_lang: str, target_lang: str) -> str:
        for src, tgt in self._get_pairs(source_lang, target_lang):
            pattern = re.compile(re.escape(str(src)), re.IGNORECASE)
            text = pattern.sub(str(tgt), text)
        return text

    def highlight_terms(self, text: str, source_lang: str, target_lang: str) -> str:
        """Wrap known medical terms in <mark class='medical-term'> tags."""
        if self._df is None:
            return text

        mask = (
            (self._df["source_lang"].str.upper() == source_lang.upper()) &
            (self._df["target_lang"].str.upper() == target_lang.upper())
        )
        terms = self._df[mask]["source_term"].tolist()

        for term in terms:
            pattern = re.compile(r"(?<!\w)" + re.escape(str(term)) + r"(?!\w)", re.IGNORECASE)
            replacement = f"<mark class='medical-term'>{term}</mark>"
            text = pattern.sub(replacement, text)

        return text

    def highlight_translated_terms(self, text: str, source_lang: str, target_lang: str) -> str:
        """Wrap translated medical terms in <mark class='medical-term'> tags."""
        if self._df is None:
            return text

        mask = (
            (self._df["source_lang"].str.upper() == source_lang.upper()) &
            (self._df["target_lang"].str.upper() == target_lang.upper())
        )
        terms = self._df[mask]["target_term"].tolist()

        for term in terms:
            pattern = re.compile(r"(?<!\w)" + re.escape(str(term)) + r"(?!\w)", re.IGNORECASE)
            replacement = f"<mark class='medical-term'>{term}</mark>"
            text = pattern.sub(replacement, text)

        return text


glossary_service = GlossaryService()
