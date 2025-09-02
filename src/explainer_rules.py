import re, tldextract
from urllib.parse import urlparse

URGENT = r"\b(urgent|immediately|verify now|reset|overdue|suspend|last chance|act now|24 hours)\b"
CRED = r"\b(password|passcode|2fa|login|ssn|bank|account verify|credentials|confirm identity)\b"
SHORTENERS = r"(bit\.ly|t\.co|goo\.gl|tinyurl\.com|ow\.ly|is\.gd|buff\.ly)"
RISK_ATTACH = r"\.(zip|exe|scr|js|html|htm|xlsm|docm)\b"

URL_REGEX = re.compile(r"https?://[^\s<>\]')]+", re.I)

def extract_urls(text:str):
    return URL_REGEX.findall(text or "")

def domain(host):
    if not host: return None
    ext = tldextract.extract(host)
    return ".".join([p for p in [ext.domain, ext.suffix] if p])

def sender_display_mismatch(headers:str, body:str):
    """
    Very light heuristic:
    - Pull 'From:' like: From: "Netflix Billing" <alerts@random.io>
    - If display brand (netflix, microsoft, bankofamerica, paypal) not in email domain -> flag
    - If any link domain != sender domain -> flag mismatch
    """
    import re
    m = re.search(r"^From:\s*(?P<disp>\"?[^\n<\"]+\"?)\s*<(?P<addr>[^>]+)>", headers, flags=re.I|re.M)
    if not m:
        return False, None, None
    disp = m.group("disp") or ""
    addr = m.group("addr") or ""
    sender_host = addr.split("@")[-1].strip().lower()
    sd = domain(sender_host)
    # brand keywords we care about
    brands = ["netflix","microsoft","paypal","apple","bank","amazon","google","intuit","dhl","ups","usps"]
    disp_l = disp.lower()
    looks_like_brand = any(b in disp_l for b in brands)
    brand_mismatch = looks_like_brand and (sd and all(b not in sd for b in brands if b in disp_l))
    # link vs sender domain mismatch (if any link domain differs strongly)
    urls = extract_urls(headers + "\n" + body)
    link_hosts = list({domain(urlparse(u).hostname) for u in urls if urlparse(u).hostname})
    link_mismatch = any(h and sd and h != sd for h in link_hosts)
    return (brand_mismatch or link_mismatch), sd, link_hosts

def explain(text:str, headers:str=""):
    urls = extract_urls(headers + "\n" + text)
    cues = []

    if re.search(URGENT, text, flags=re.I): cues.append("Urgency language")
    if re.search(CRED, text, flags=re.I): cues.append("Credentials requested")
    if re.search(SHORTENERS, text, flags=re.I): cues.append("URL shortener detected")
    if re.search(RISK_ATTACH, text, flags=re.I): cues.append("Risky attachment type mentioned")

    mism, sd, links = sender_display_mismatch(headers, text)
    if mism: cues.append("Sender/display vs link domain mismatch")

    return {"cues": cues, "urls": urls}
