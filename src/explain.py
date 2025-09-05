def explain(text: str, headers: str = ""):
    urls = extract_urls(headers + "\n" + text)

    phishing_cues = []
    safe_notes = []

    # Text-based phishing cues
    if re.search(URGENT, text, flags=re.I): 
        phishing_cues.append("Urgency language")
    if re.search(CRED, text, flags=re.I): 
        phishing_cues.append("Credentials requested")
    if re.search(RISK_ATTACH, text, flags=re.I): 
        phishing_cues.append("Risky attachment type mentioned")

    # URL checks
    for u in urls:
        host = (urlparse(u).hostname or "").lower()

        # shorteners: host-based only
        if host in SHORTENER_HOSTS:
            phishing_cues.append(f"URL shortener detected ({host})")

        # safe-domain note
        if host in SAFE_DOMAINS:
            safe_notes.append(f"Safe domain recognized: {host}")

    # Sender/display mismatch
    mism, sd, links = sender_display_mismatch(headers, text)
    if mism: 
        phishing_cues.append("Sender/display vs link domain mismatch")

    # phishing cues first, safe notes last
    cues = phishing_cues + safe_notes

    return {"cues": cues, "urls": urls}

