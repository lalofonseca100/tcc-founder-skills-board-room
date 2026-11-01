#!/usr/bin/env python3
"""polite_fetch.py - respectful web fetcher for founder-cto research (stdlib only).

- Checks robots.txt before every URL and skips disallowed pages.
- Waits between requests to the same host (default 3 s).
- Identifies itself with a clear User-Agent.
- Saves each page as plain text + a ledger row (url, title, date fetched, sha256)
  so every fact in a report can be traced to a dated copy.

Usage:
  python3 -I polite_fetch.py --out founder/cto/sources URL [URL ...]
  python3 -I polite_fetch.py --out founder/cto/sources --list urls.txt
Never use it to log in, bypass paywalls or CAPTCHAs, or collect personal data.
"""
import argparse, csv, datetime, hashlib, html.parser, os, re, sys, time
import urllib.error, urllib.parse, urllib.request, urllib.robotparser

UA = "FounderSkills-Research-Bot/1.0 (+founder research; contact via site owner)"

class _Text(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "header"}
    def __init__(self):
        super().__init__(); self.parts = []; self.title = ""; self._skip = 0; self._in_title = False; self.links = []
    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP: self._skip += 1
        if tag == "title": self._in_title = True
        if tag == "a":
            href = dict(attrs).get("href")
            if href: self.links.append(href)
        if tag in ("p", "br", "li", "h1", "h2", "h3", "h4", "tr", "div"): self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip: self._skip -= 1
        if tag == "title": self._in_title = False
    def handle_data(self, data):
        if self._in_title: self.title += data
        elif not self._skip: self.parts.append(data)

_robots, _last = {}, {}

def allowed(url):
    """True / False from robots.txt, or None when robots.txt could not be read."""
    p = urllib.parse.urlparse(url); base = f"{p.scheme}://{p.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                rp.parse(r.read().decode("utf-8", "replace").splitlines())
        except urllib.error.HTTPError as e:
            if e.code in (404, 410): rp.allow_all = True   # no robots.txt: allowed
            else: rp = None                                   # blocked/unknown
        except Exception:
            rp = None
        _robots[base] = rp
    rp = _robots[base]
    return None if rp is None else rp.can_fetch(UA, url)

def fetch(url, delay):
    host = urllib.parse.urlparse(url).netloc
    wait = delay - (time.time() - _last.get(host, 0))
    if wait > 0: time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,text/plain"})
    with urllib.request.urlopen(req, timeout=30) as r:
        _last[host] = time.time()
        raw = r.read(5_000_000); ctype = r.headers.get("Content-Type", "")
        charset = r.headers.get_content_charset() or "utf-8"
    return raw, ctype, charset

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="*"); ap.add_argument("--list")
    ap.add_argument("--out", default="founder/cto/sources")
    ap.add_argument("--delay", type=float, default=3.0)
    ap.add_argument("--robots-only", action="store_true",
                    help="only check robots.txt; exit 0 allowed, 2 disallowed, 3 unreadable")
    a = ap.parse_args()
    if a.robots_only:
        codes = []
        for url in a.urls:
            ok = allowed(url); codes.append(0 if ok else (3 if ok is None else 2))
            print({True: "allowed", False: "disallowed", None: "unreadable"}[ok], url)
        return max(codes or [0])
    urls = list(a.urls)
    if a.list: urls += [l.strip() for l in open(a.list) if l.strip() and not l.startswith("#")]
    if not urls: ap.error("give at least one URL")
    os.makedirs(a.out, exist_ok=True)
    ledger = os.path.join(a.out, "ledger.csv"); new = not os.path.exists(ledger)
    with open(ledger, "a", newline="") as fh:
        w = csv.writer(fh)
        if new: w.writerow(["fetched_utc", "status", "url", "title", "file", "sha256", "links_found"])
        for url in urls:
            now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
            ok = allowed(url)
            if ok is None:
                w.writerow([now, "skipped-robots-unreadable", url, "", "", "", 0]); print("SKIP robots.txt unreadable:", url); continue
            if not ok:
                w.writerow([now, "skipped-robots", url, "", "", "", 0]); print("SKIP robots:", url); continue
            try: raw, ctype, cs = fetch(url, a.delay)
            except Exception as e:
                w.writerow([now, f"error:{type(e).__name__}", url, "", "", "", 0]); print("ERR", url, e); continue
            text = raw.decode(cs, "replace"); title, links = "", 0
            if "html" in ctype:
                p = _Text(); p.feed(text); title = p.title.strip(); links = len(p.links)
                text = re.sub(r"\n\s*\n+", "\n\n", "".join(p.parts)).strip()
            sha = hashlib.sha256(raw).hexdigest()
            fname = sha[:12] + ".txt"
            with open(os.path.join(a.out, fname), "w") as out:
                out.write(f"URL: {url}\nTITLE: {title}\nFETCHED: {now}\n\n{text}\n")
            w.writerow([now, "ok", url, title, fname, sha, links]); print("OK", url, "->", fname)

if __name__ == "__main__":
    sys.exit(main())
