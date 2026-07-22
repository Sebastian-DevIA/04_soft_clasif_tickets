import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.loader import load_sentiment_dataset
from src.nlp.classifier import evaluate, save_model, train


def main() -> None:
    df = load_sentiment_dataset()

    print("Entrenando con", len(df[df["split"] == "train"]), "ejemplos...")
    pipeline = train(df)

    print()
    print("Evaluación sobre el set de test:")
    print(evaluate(pipeline, df))

    save_model(pipeline)
    print("Modelo guardado en models/sentiment_classifier.joblib")


if __name__ == "__main__":
    main()
