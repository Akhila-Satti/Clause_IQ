import pandas as pd

from config import (
    DATA_FILE,
    TEXT_COLUMN,
    LABEL_COLUMN,
    SPLIT_COLUMN,
    CATEGORIES,
)


def load_dataset():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    required_columns = [
        TEXT_COLUMN,
        LABEL_COLUMN,
        SPLIT_COLUMN
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Missing column: {column}"
            )

    # Check missing values
    if df[required_columns].isnull().any().any():
        raise ValueError(
            "Dataset contains missing values."
        )

    # Clean whitespace
    df[TEXT_COLUMN] = (
        df[TEXT_COLUMN].astype(str).str.strip()
    )

    df[LABEL_COLUMN] = (
        df[LABEL_COLUMN].astype(str).str.strip()
    )

    df[SPLIT_COLUMN] = (
        df[SPLIT_COLUMN].astype(str).str.strip().str.lower()
    )

    # Validate labels
    unknown_labels = (
        set(df[LABEL_COLUMN].unique()) - set(CATEGORIES)
    )

    if unknown_labels:
        raise ValueError(
            f"Unknown categories: {unknown_labels}"
        )

    # Validate split names
    valid_splits = {"train", "val", "test"}

    if not set(df[SPLIT_COLUMN].unique()).issubset(valid_splits):
        raise ValueError("Invalid split names found.")

    print("\nDataset loaded successfully!")

    print("\nTotal records:", len(df))

    print("\nSplit distribution:")
    print(df[SPLIT_COLUMN].value_counts())

    print("\nCategory distribution:")
    print(df[LABEL_COLUMN].value_counts())

    print("\nCategory distribution across splits:")
    print(pd.crosstab(df[SPLIT_COLUMN], df[LABEL_COLUMN]))

    # Check exact normalized duplicates across splits
    normalized = (
        df[TEXT_COLUMN]
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    duplicate_rows = df[
        normalized.duplicated(keep=False)
    ]

    if not duplicate_rows.empty:
        duplicate_groups = pd.DataFrame({
            "text": normalized,
            "split": df[SPLIT_COLUMN]
        })

        cross_split = (
            duplicate_groups.groupby("text")["split"]
            .nunique()
            .gt(1)
            .sum()
        )

        print(
            "\nWarning: normalized duplicate groups found:",
            cross_split
        )

    return df


def get_splits(df):

    train_df = df[
        df[SPLIT_COLUMN] == "train"
    ]

    val_df = df[
        df[SPLIT_COLUMN] == "val"
    ]

    test_df = df[
        df[SPLIT_COLUMN] == "test"
    ]

    for name, part in [
        ("Training", train_df),
        ("Validation", val_df),
        ("Testing", test_df)
    ]:

        if part.empty:
            raise ValueError(
                f"{name} dataset is empty."
            )

        missing = (
            set(CATEGORIES) - set(part[LABEL_COLUMN])
        )

        if missing:
            raise ValueError(
                f"{name} dataset missing categories: {missing}"
            )

    return train_df, val_df, test_df