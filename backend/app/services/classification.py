from src.nlp.classifier import MODEL_VERSION, load_model, predict_one

# El modelo se carga una sola vez al importar el módulo (singleton): leer el
# .joblib en cada request sería un desperdicio de I/O y de CPU.
_pipeline = load_model()


def classify_text(text: str) -> tuple[str, float]:
    return predict_one(_pipeline, text)


__all__ = ["MODEL_VERSION", "classify_text"]
