from pathlib import Path

import pandas as pd
from datasets import load_dataset

RAW_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "tweet_sentiment_es.csv"

LABEL_NAMES = ["negative", "neutral", "positive"]


def download_sentiment_dataset() -> pd.DataFrame:
    dataset = load_dataset(
        "cardiffnlp/tweet_sentiment_multilingual",
        revision="refs/convert/parquet",
        data_files={
            "train": "spanish/train/0000.parquet",
            "validation": "spanish/validation/0000.parquet",
            "test": "spanish/test/0000.parquet",
        },
    )

    frames = []
    for split_name, split_data in dataset.items():
        frame = split_data.to_pandas()
        frame["split"] = split_name
        frames.append(frame)

    df = pd.concat(frames, ignore_index=True)
    df["sentiment"] = df["label"].map(dict(enumerate(LABEL_NAMES)))
    return df


def load_sentiment_dataset() -> pd.DataFrame:
    # Se cachea en disco para no depender de internet/Hugging Face cada vez que exploremos o entrenemos.
    if RAW_DATA_PATH.exists():
        return pd.read_csv(RAW_DATA_PATH)

    df = download_sentiment_dataset()
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DATA_PATH, index=False)
    return df
