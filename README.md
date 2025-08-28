# Phishing Email Classifier + Explainer

Demo project for career fair.

- Train a baseline classifier (TF-IDF + Logistic Regression).
- Add simple rule-based explanations highlighting phishing cues.
- Show ROC curve + confusion matrix.

## Quickstart

```bash
python -m venv .venv
# activate venv
pip install -r requirements.txt
python -m src.train --data data/raw --out data/processed
```

Export notebooks to HTML for iPad demo.
