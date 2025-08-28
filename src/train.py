import argparse
from pathlib import Path
import joblib, matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, RocCurveDisplay, ConfusionMatrixDisplay
from sklearn.pipeline import make_pipeline
from .data import load_dataset, make_splits

def main(args):
    df = load_dataset(args.data)
    train, val, test = make_splits(df)
    pipe = make_pipeline(TfidfVectorizer(max_features=20000, ngram_range=(1,2)),
                         LogisticRegression(max_iter=200))
    pipe.fit(train["text"], train["label"])
    proba = pipe.predict_proba(test["text"])[:,1]
    auc = roc_auc_score((test["label"]=="phish").astype(int), proba)
    print("AUC:", auc)
    RocCurveDisplay.from_predictions((test["label"]=="phish").astype(int), proba)
    plt.savefig("reports/figures/roc.png")
    plt.clf()
    ConfusionMatrixDisplay.from_estimator(pipe, test["text"], test["label"])
    plt.savefig("reports/figures/cm.png")
    Path(args.out).mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, Path(args.out)/"model.joblib")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/raw")
    p.add_argument("--out", default="data/processed")
    main(p.parse_args())
