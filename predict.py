import argparse, json, sys
from pathlib import Path
from email import policy
from email.parser import BytesParser

import joblib
import matplotlib.pyplot as plt
from src.explainer_rules import explain

# ---- Config ----
MODEL_PATH = Path("models/model.joblib")

def load_model():
    if not MODEL_PATH.exists():
        sys.exit("ERROR: model.joblib not found in models/")
    return joblib.load(MODEL_PATH)  # pipeline = TF-IDF + LogisticRegression

def read_text_from_file(fp: Path):
    if fp.suffix.lower() == ".eml":
        with open(fp, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)
        headers = []
        for k in ["From","To","Subject","Date","Reply-To"]:
            v = msg.get(k)
            if v: headers.append(f"{k}: {v}")
        headers_str = "\n".join(headers)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_content()
        else:
            body = msg.get_content() if msg.get_content_type()=="text/plain" else ""
        return headers_str, body
    else:
        text = fp.read_text(encoding="utf-8", errors="ignore")
        return "", text

def classify(pipe, text: str, threshold: float):
    prob = float(pipe.predict_proba([text])[0,1])  # prob of phish
    label = "Phish" if prob >= threshold else "Safe"
    return label, prob

def pretty_print(res):
    print("== RESULT ==")
    print(f"Label: {res['label']}")

    # probability bar
    bar_len = 20
    filled = int(res['prob'] * bar_len)
    bar = "█" * filled + "-" * (bar_len - filled)
    print(f"Confidence: [{bar}] {res['prob']:.1%}")

    cues = res["explain"].get("cues", [])
    urls = res["explain"].get("urls", [])
    if cues:
        print("Why:")
        for c in cues:
            print(f"  - {c}")
        print(f"Top suspicious cue: {cues[0]}")
    if urls:
        print("URLs:")
        for u in urls:
            print(f"  - {u}")

def main():
    ap = argparse.ArgumentParser(description="Phishing classifier + explainer")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="Raw email text to classify")
    g.add_argument("--file", help="Path to a .eml or .txt")
    g.add_argument("--dir",  help="Directory of .eml/.txt for batch mode")
    ap.add_argument("--json_out", help="Write JSON result(s) to this path")
    ap.add_argument("--threshold", type=float, default=0.5,
                    help="Probability cutoff for labeling as phish")
    args = ap.parse_args()

    pipe = load_model()

    if args.text:
        headers, body = "", args.text
        label, prob = classify(pipe, body, args.threshold)
        exp = explain(body, headers)
        res = {"label": label, "prob": prob, "explain": exp}
        pretty_print(res)
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(res, indent=2), encoding="utf-8")
        return

    if args.file:
        fp = Path(args.file)
        headers, body = read_text_from_file(fp)
        label, prob = classify(pipe, headers + "\n" + body, args.threshold)
        exp = explain(body, headers)
        res = {"file": fp.name, "label": label, "prob": prob, "explain": exp}
        pretty_print(res)
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(res, indent=2), encoding="utf-8")
        return

    if args.dir:
        dp = Path(args.dir)
        files = sorted([p for p in dp.glob("**/*") if p.suffix.lower() in [".eml",".txt"]])
        results = []
        for fp in files:
            headers, body = read_text_from_file(fp)
            label, prob = classify(pipe, headers + "\n" + body, args.threshold)
            exp = explain(body, headers)
            results.append({"file": fp.name, "label": label, "prob": prob, "explain": exp})
        print("file,label,prob")
        for r in results:
            print(f"{r['file']},{r['label']},{r['prob']:.4f}")
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(results, indent=2), encoding="utf-8")
        out_csv = Path("demo_assets/predictions.csv")
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        with open(out_csv, "w", encoding="utf-8") as f:
            f.write("file,label,prob\n")
            for r in results:
                f.write(f"{r['file']},{r['label']},{r['prob']:.6f}\n")

        # Batch summary pie chart
        counts = {"Phish": 0, "Safe": 0}
        for r in results:
            counts[r["label"]] += 1
        plt.figure()
        plt.pie(counts.values(), labels=counts.keys(), autopct="%1.1f%%")
        plt.title("Batch Results")
        plt.savefig("demo_assets/batch_summary.png")
        plt.close()

if __name__ == "__main__":
    main()
