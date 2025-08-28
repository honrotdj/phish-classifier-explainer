from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

def load_dataset(raw_dir: str):
    raw = Path(raw_dir)
    csvs = list(raw.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError("Put CSV with 'text','label' in data/raw/")
    df = pd.read_csv(csvs[0])
    return df

def make_splits(df, test_size=0.2, val_size=0.1, seed=42):
    train, test = train_test_split(df, test_size=test_size, stratify=df['label'], random_state=seed)
    train, val = train_test_split(train, test_size=val_size, stratify=train['label'], random_state=seed)
    return train, val, test
