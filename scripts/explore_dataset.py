import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.loader import load_sentiment_dataset


def main() -> None:
    df = load_sentiment_dataset()

    print("Forma del dataset (filas, columnas):", df.shape)
    print()

    print("Primeras filas:")
    print(df[["text", "sentiment", "split"]].head())
    print()

    print("Valores nulos por columna:")
    print(df.isna().sum())
    print()

    print("Distribución de sentimiento (todo el dataset):")
    print(df["sentiment"].value_counts())
    print()

    print("Distribución de sentimiento (solo train):")
    print(df[df["split"] == "train"]["sentiment"].value_counts())
    print()

    df["text_length"] = df["text"].str.len()
    print("Estadísticas de longitud de texto (caracteres):")
    print(df["text_length"].describe())


if __name__ == "__main__":
    main()
