import re, tldextract

def explain(text):
    cues = []
    if re.search(r"urgent|immediately|verify now", text, re.I):
        cues.append("Urgency language")
    if re.search(r"password|login|verify identity", text, re.I):
        cues.append("Credentials requested")
    urls = re.findall(r"https?://\S+", text)
    if urls: cues.append(f"Contains {len(urls)} link(s)")
    return {"cues": cues, "urls": urls}
