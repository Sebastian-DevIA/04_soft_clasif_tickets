# src/data/

Adquisición del dataset de entrenamiento.

- `loader.py`: descarga el dataset público `cardiffnlp/tweet_sentiment_multilingual` (split en español) desde Hugging Face, lo combina en un único `DataFrame` de pandas con columna `split` (train/validation/test) y `sentiment` (negative/neutral/positive), y lo cachea en `data/raw/tweet_sentiment_es.csv`. `load_sentiment_dataset()` es el punto de entrada: usa el cache si existe, o descarga si no.
