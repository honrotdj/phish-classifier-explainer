======================================
PHISHING CLASSIFIER – DEMO INSTRUCTIONS
======================================

This demo shows how our AI detects phishing emails in real time.

1. Open Command Prompt.
2. Navigate to the project folder:
   cd C:\Users\dhonr\OneDrive\Documents\phish_classifier_explainer
3. Run the demo menu:
   scan_demo.bat

4. You will see a list of available sample files (in demo_assets\samples).
5. Type the filename you want to scan (example: sample_phish_01.txt).
6. The classifier will show:
   - File scanned
   - Prediction (Phish or Safe)
   - Confidence bar
   - Suspicious cues and URLs (if any)

7. Type Q to quit the demo.

Tips:
- Add your own .txt emails into demo_assets\samples to scan them.
- Keep filenames simple (no spaces).
- Threshold can be changed in predict.py (default is 0.7).
- Model performance plots (ROC, Confusion Matrix) are in demo_assets/plots.


