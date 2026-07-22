from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline

from src.nlp.preprocess import SPANISH_STOPWORDS, clean_text

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "models" / "sentiment_classifier.joblib"
MODEL_VERSION = "tfidf-logreg-v1"


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    preprocessor=clean_text,
                    stop_words=SPANISH_STOPWORDS,
                    ngram_range=(1, 2),
                    min_df=2,
                ),
            ),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )


def train(df: pd.DataFrame) -> Pipeline:
    train_df = df[df["split"] == "train"]
    pipeline = build_pipeline()
    pipeline.fit(train_df["text"], train_df["sentiment"])
    return pipeline


def evaluate(pipeline: Pipeline, df: pd.DataFrame) -> str:
    test_df = df[df["split"] == "test"]
    predictions = pipeline.predict(test_df["text"])
    return classification_report(test_df["sentiment"], predictions)


def save_model(pipeline: Pipeline) -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)


def load_model() -> Pipeline:
    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"No se encontró un modelo entrenado en {MODEL_PATH}. "
            "Corre 'python scripts/train_model.py' primero."
        )
    return joblib.load(MODEL_PATH)


def predict_one(pipeline: Pipeline, text: str) -> tuple[str, float]:
    proba = pipeline.predict_proba([text])[0]
    best_idx = proba.argmax()
    return pipeline.classes_[best_idx], float(proba[best_idx])
