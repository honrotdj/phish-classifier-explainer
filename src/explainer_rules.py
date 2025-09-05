import re, tldextract
from urllib.parse import urlparse

# Regex patterns
URGENT = r"\b(urgent|immediately|verify now|reset|overdue|suspend|last chance|act now|24 hours)\b"
CRED = r"\b(password|passcode|2fa|login|ssn|bank|account verify|credentials|confirm identity)\b"
RISK_ATTACH = r"\.(zip|exe|scr|js|html|htm|xlsm|docm)\b"

# Shorteners to flag by host (exact match only)
SHORTENER_HOSTS = {
    "bit.ly", "t.co", "goo.gl", "tinyurl.com", "ow.ly", "is.gd", "buff.ly"
}

# Safe, common legit hosts (some exact, some suffix rules like ".sharepoint.com")
SAFE_DOMAINS = {
    "drive.google.com",
    "docs.google.com",
    "calendar.google.com",
    "photos.google.com",
    ".sharepoint.com",           # suffix match for SharePoint Online tenants
    "outlook.office.com",
    "teams.microsoft.com",
    "docusign.net",
    "amazon.com",
    "paypal.com",
    "stripe.com",
    "starbucks.com",
    "dropbox.com",
    "slack.com",
    "zoom.us",
    "fedex.com",
    "ups.com",
    "usps.com"
}

# URL regex
URL_REGEX = re.compile(r"https?://[^\s<>\]')]+", re.I)

def extract_urls(text: str):
    return URL_REGEX.findall(text or "")

def domain(host):
    if not host:
        return None
    ext = tldextract.extract(host)
    return ".".join([p for p in [ext.domain, ext.suffix] if p])

def is_safe_host(host: str) -> bool:
    host = (host or "").lower()
    for d in SAFE_DOMAINS:
        d = d.lower()
        if d.startswith("."):
            # suffix rule, e.g. ".sharepoint.com" matches "contoso.sharepoint.com"
            if host.endswith(d):
                return True
        else:
            # exact host rule
            if host == d:
                return True
    return False

def sender_display_mismatch(headers: str, body: str):
    m = re.search(r"^From:\s*(?P<disp>\"?[^\n<\"]+\"?)\s*<(?P<addr>[^>]+)>", headers, flags=re.I | re.M)
    if not m:
        return False, None, None
    disp = m.group("disp") or ""
    addr = m.group("addr") or ""
    sender_host = addr.split("@")[-1].strip().lower()
    sd = domain(sender_host)
    brands = ["netflix","microsoft","paypal","apple","bank","amazon","google","intuit","dhl","ups","usps"]
    disp_l = disp.lower()
    looks_like_brand = any(b in disp_l for b in brands)
    brand_mismatch = looks_like_brand and (sd and all(b not in sd for b in brands if b in disp_l))
    urls = extract_urls(headers + "\n" + body)
    link_hosts = list({domain(urlparse(u).hostname) for u in urls if urlparse(u).hostname})
    link_mismatch = any(h and sd and h != sd for h in link_hosts)
    return (brand_mismatch or link_mismatch), sd, link_hosts

def explain(text: str, headers: str = ""):
    urls = extract_urls(headers + "\n" + text)

    phishing_cues = []
    safe_notes = []

    # Text-based cues
    if re.search(URGENT, text, flags=re.I): 
        phishing_cues.append("Urgency language")
    if re.search(CRED, text, flags=re.I): 
        phishing_cues.append("Credentials requested")
    if re.search(RISK_ATTACH, text, flags=re.I): 
        phishing_cues.append("Risky attachment type mentioned")

    # URL checks
    for u in urls:
        host = (urlparse(u).hostname or "").lower()

        # shorteners
        if host in SHORTENER_HOSTS:
            phishing_cues.append(f"URL shortener detected ({host})")

        # safe-domain note
        if is_safe_host(host):
            safe_notes.append(f"Safe domain recognized: {host}")

    # Sender/display mismatch
    mism, sd, links = sender_display_mismatch(headers, text)
    if mism: 
        phishing_cues.append("Sender/display vs link domain mismatch")

    # phishing cues first, safe notes last
    cues = phishing_cues + safe_notes

    return {"cues": cues, "urls": urls}
