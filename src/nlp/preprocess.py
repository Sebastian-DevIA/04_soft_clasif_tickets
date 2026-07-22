import re

import spacy

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_MENTION_RE = re.compile(r"@\w+")
_MULTI_SPACE_RE = re.compile(r"\s+")

# Se carga una sola vez al importar el módulo: crear el pipeline de spaCy es costoso,
# y aquí solo necesitamos su lista de stopwords en español, no el pipeline completo.
_nlp = spacy.load("es_core_news_sm", disable=["parser", "ner", "tagger", "lemmatizer"])

# Las negaciones NO deben tratarse como stopwords: son la señal más importante
# para el sentimiento ("no me gusta" pierde el sentido si se elimina "no").
NEGATION_WORDS = {"no", "nada", "nunca", "ni", "sin", "tampoco", "jamas", "jamás", "nadie", "ningun", "ningún", "ninguno", "ninguna"}
SPANISH_STOPWORDS = [w for w in _nlp.Defaults.stop_words if w not in NEGATION_WORDS]


def clean_text(text: str) -> str:
    text = text.lower()
    text = _URL_RE.sub(" ", text)
    text = _MENTION_RE.sub(" ", text)
    text = _MULTI_SPACE_RE.sub(" ", text).strip()
    return text
