# models/

Modelos entrenados serializados con `joblib` (no versionados, solo `.gitkeep`). Se generan corriendo `scripts/train_model.py`, que guarda `sentiment_classifier.joblib` (pipeline completo: TF-IDF + Logistic Regression). Se cargan en la API vía `src/nlp/classifier.py::load_model()`.
