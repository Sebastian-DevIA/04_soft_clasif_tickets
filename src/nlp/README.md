# src/nlp/

Preprocesamiento y clasificación de texto.

- `preprocess.py`: `clean_text()` normaliza el texto (minúsculas, quita URLs y menciones `@usuario`) y expone `SPANISH_STOPWORDS`, la lista de stopwords en español de spaCy **excluyendo negaciones** ("no", "nada", "nunca", etc.) — quitarlas destruiría la señal de sentimiento (ver `docs/DECISIONES.md`, Hito 2-3).
- `classifier.py`: `build_pipeline()` arma un pipeline de scikit-learn (TF-IDF + Logistic Regression); `train()` y `evaluate()` entrenan/miden sobre los splits del dataset; `save_model()`/`load_model()` serializan el pipeline completo a `models/sentiment_classifier.joblib`; `predict_one()` devuelve `(sentimiento, confianza)` para un texto nuevo — es la función que consume la API.
