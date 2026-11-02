#!/usr/bin/env python3
"""source_ingest.py - turn a source into a dated, traceable text copy for founder-research.

Handles the kinds polite_fetch.py does not:
  - YouTube videos: captions only (never the video), via yt-dlp. Human captions
    are preferred over auto-generated ones; the choice is recorded.
  - PDFs (papers, reports, book summaries) from a URL or a local file, via pdftotext.
  - arXiv pages: official metadata from the arXiv API, then the PDF.
  - Local text files the founder uploads (.txt, .md, .vtt, .srt): transcripts, notes, exports.
Web pages: use founder-cto's polite_fetch.py or render_fetch.js instead.

Each source gets <out>/<slug>/text.md + meta.json, and a row in <out>/ledger.csv:
date, source, kind, method, status (opened / partial / failed), sha256, words, note.
It never logs in, never bypasses paywalls or bot blocks, and never downloads video.

Usage:
  python3 -I source_ingest.py --out founder/research/sources URL_OR_FILE [...]
  python3 -I source_ingest.py --out founder/research/sources --ytdlp "python3 -m yt_dlp" URL
yt-dlp is optional and only needed for YouTube (pip install yt-dlp; tested with
2025.10.22). YouTube changes often: if captions fail, update yt-dlp or ask the founder to
paste the transcript (YouTube: "...more" > "Show transcript").
"""
import argparse, csv, datetime, glob, hashlib, json, os, re, shlex, subprocess, sys, tempfile, time
import urllib.parse, urllib.request
import xml.etree.ElementTree as ET

UA = "FounderSkills-Research-Bot/1.0 (+founder research; contact via site owner)"
TODAY = datetime.date.today().isoformat()
MIN_WORDS = 300  # below this a copy is "partial": probably a stub, not the whole source


def slugify(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return (s[:60] or "source") + "-" + hashlib.sha1(s.encode()).hexdigest()[:6]


def http_get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")


def kind_of(src):
    if os.path.exists(src):
        ext = os.path.splitext(src)[1].lower()
        return "pdf-file" if ext == ".pdf" else "text-file"
    host = urllib.parse.urlparse(src).netloc.lower()
    if "youtube.com" in host or host == "youtu.be":
        return "youtube"
    if host.endswith("arxiv.org"):
        return "arxiv"
    if urllib.parse.urlparse(src).path.lower().endswith(".pdf"):
        return "pdf-url"
    return "web"


def clean_vtt(raw):
    """VTT/SRT -> paragraphs with a [mm:ss] mark about every 30 s; drops the
    rolling duplicate lines that auto-captions repeat."""
    out, last_line, last_mark, para = [], "", -999, []
    t = 0
    for line in raw.splitlines():
        m = re.match(r"(\d+):(\d\d):(\d\d)[.,]\d+\s+-->", line) or re.match(r"(\d\d):(\d\d)[.,]\d+\s+-->", line)
        if m:
            g = [int(x) for x in m.groups()]
            t = g[0] * 3600 + g[1] * 60 + g[2] if len(g) == 3 else g[0] * 60 + g[1]
            continue
        if not line.strip() or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or line.strip().isdigit():
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if not line or line == last_line:
            continue
        last_line = line
        if t - last_mark >= 30:
            if para:
                out.append(" ".join(para)); para = []
            para.append(f"[{t // 60:02d}:{t % 60:02d}]")
            last_mark = t
        para.append(line)
    if para:
        out.append(" ".join(para))
    return "\n\n".join(out)


def ingest_youtube(src, ytdlp, tmp):
    if not ytdlp:
        raise RuntimeError("yt-dlp not available: install it, or ask the founder to paste the transcript")
    base = shlex.split(ytdlp)
    r = subprocess.run(base + ["-J", "--skip-download", src], capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        err = [l for l in r.stderr.splitlines() if l.startswith("ERROR")] or r.stderr.splitlines()[-1:] or ["unknown"]
        if "not a bot" in err[-1] or "Sign in" in err[-1]:
            raise RuntimeError("YouTube bot check (blocks cloud servers): do not bypass; use the YouTube "
                               "ladder (official transcript, the founder's paste, or yt-dlp on the founder's device)")
        raise RuntimeError(err[-1][:200])
    info = json.loads(r.stdout)
    human = info.get("subtitles") or {}
    auto = info.get("automatic_captions") or {}
    lang_pref = [info.get("language") or "", "en", "es", "nl"]
    pick = None
    for pool, label in ((human, "human"), (auto, "auto")):
        for lang in lang_pref + sorted(pool):
            if lang and any(k == lang or k.startswith(lang + "-") for k in pool):
                pick = (next(k for k in pool if k == lang or k.startswith(lang + "-")), label); break
        if pick:
            break
    if not pick:
        raise RuntimeError("video has no captions: ask the founder for a transcript or notes")
    lang, label = pick
    flag = "--write-subs" if label == "human" else "--write-auto-subs"
    subprocess.run(base + ["--skip-download", flag, "--sub-langs", lang, "--sub-format", "vtt",
                           "-o", os.path.join(tmp, "sub"), src], capture_output=True, text=True,
                   timeout=180, check=True)
    files = glob.glob(os.path.join(tmp, "sub*.vtt"))
    if not files:
        raise RuntimeError("captions listed but not downloaded (YouTube may have changed; update yt-dlp)")
    text = clean_vtt(open(files[0], encoding="utf-8", errors="replace").read())
    up = info.get("upload_date") or ""
    meta = {"title": info.get("title"), "author": info.get("channel") or info.get("uploader"),
            "published": f"{up[:4]}-{up[4:6]}-{up[6:]}" if len(up) == 8 else None,
            "duration_min": round((info.get("duration") or 0) / 60, 1),
            "views": info.get("view_count"), "captions": f"{label} ({lang})",
            "description": (info.get("description") or "")[:1500]}
    note = "auto-generated captions: names and numbers may be misheard" if label == "auto" else ""
    return text, meta, f"yt-dlp captions ({label})", note


def pdf_to_text(path):
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"], capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError("pdftotext failed: " + r.stderr.strip()[:200])
    pages = r.stdout.count("\f") + 1
    return r.stdout.replace("\f", "\n\n"), pages


def ingest_pdf_url(src, tmp):
    data, ctype = http_get(src)
    if b"%PDF" not in data[:1024]:
        raise RuntimeError(f"not a PDF (got {ctype or 'unknown type'}): maybe a login or paywall page")
    p = os.path.join(tmp, "doc.pdf"); open(p, "wb").write(data)
    text, pages = pdf_to_text(p)
    return text, {"pages": pages}, "download + pdftotext", ""


def ingest_arxiv(src, tmp):
    m = re.search(r"arxiv\.org/(?:abs|pdf|html)/([^?#/]+(?:/[^?#/]+)?)", src)
    if not m:
        raise RuntimeError("could not read the arXiv id from the URL")
    aid = re.sub(r"(\.pdf|v\d+)$", "", m.group(1))
    xml, _ = http_get("https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(aid))
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    e = ET.fromstring(xml).find("a:entry", ns)
    if e is None or e.find("a:title", ns) is None:
        raise RuntimeError("arXiv API returned no entry for " + aid)
    g = lambda tag: (e.findtext(tag, default="", namespaces=ns) or "").strip()
    meta = {"title": re.sub(r"\s+", " ", g("a:title")),
            "author": ", ".join(a.findtext("a:name", namespaces=ns) for a in e.findall("a:author", ns)),
            "published": g("a:published")[:10], "updated": g("a:updated")[:10],
            "journal_ref": g("x:journal_ref") or None,
            "peer_reviewed": "yes (journal ref)" if g("x:journal_ref") else "not shown (preprint)",
            "abstract": re.sub(r"\s+", " ", g("a:summary"))}
    time.sleep(3)
    try:
        text, extra = ingest_pdf_url(f"https://arxiv.org/pdf/{aid}", tmp)[:2]
        meta.update(extra)
        return text, meta, "arXiv API + PDF", ""
    except Exception as ex:
        return "ABSTRACT ONLY\n\n" + meta["abstract"], meta, "arXiv API (abstract only)", f"full text failed: {ex}"


def ingest_local(src, kind):
    if kind == "pdf-file":
        text, pages = pdf_to_text(src)
        return text, {"pages": pages, "title": os.path.basename(src)}, "local file + pdftotext", ""
    raw = open(src, encoding="utf-8", errors="replace").read()
    if src.lower().endswith((".vtt", ".srt")):
        raw = clean_vtt(raw)
    return raw, {"title": os.path.basename(src)}, "local file", "provided by the founder: record where it came from"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ytdlp", default=None, help='command to run yt-dlp, e.g. "python3 -m yt_dlp"')
    ap.add_argument("sources", nargs="+")
    a = ap.parse_args()
    ytdlp = a.ytdlp
    if not ytdlp:
        if subprocess.run(["which", "yt-dlp"], capture_output=True).returncode == 0:
            ytdlp = "yt-dlp"
    os.makedirs(a.out, exist_ok=True)
    ledger = os.path.join(a.out, "ledger.csv")
    new = not os.path.exists(ledger)
    with open(ledger, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["date", "source", "kind", "method", "status", "sha256", "words", "folder", "note"])
        for src in a.sources:
            kind = kind_of(src)
            if kind == "web":
                print(f"SKIP {src}: web page, use polite_fetch.py or render_fetch.js (founder-cto)")
                w.writerow([TODAY, src, kind, "-", "skipped", "", 0, "", "use founder-cto fetch tools"])
                continue
            folder = os.path.join(a.out, slugify(src))
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    if kind == "youtube":
                        text, meta, method, note = ingest_youtube(src, ytdlp, tmp)
                    elif kind == "arxiv":
                        text, meta, method, note = ingest_arxiv(src, tmp)
                    elif kind == "pdf-url":
                        text, meta, method, note = ingest_pdf_url(src, tmp)
                    else:
                        text, meta, method, note = ingest_local(src, kind)
                except Exception as ex:
                    msg = str(ex).strip().splitlines()[-1][:200] if str(ex).strip() else type(ex).__name__
                    print(f"FAILED {src}: {msg}")
                    w.writerow([TODAY, src, kind, "-", "failed", "", 0, "", msg])
                    continue
            words = len(text.split())
            status = "opened" if words >= MIN_WORDS and "abstract only" not in method else "partial"
            sha = hashlib.sha256(text.encode()).hexdigest()
            os.makedirs(folder, exist_ok=True)
            meta.update({"source": src, "kind": kind, "method": method, "status": status,
                         "fetched": TODAY, "words": words, "sha256": sha, "note": note})
            json.dump(meta, open(os.path.join(folder, "meta.json"), "w"), indent=2, ensure_ascii=False)
            head = f"# {meta.get('title') or src}\n\nSource: {src}\nFetched: {TODAY} via {method}\n\n"
            open(os.path.join(folder, "text.md"), "w").write(head + text + "\n")
            w.writerow([TODAY, src, kind, method, status, sha, words, folder, note])
            print(f"{status.upper()} {src}: {words} words -> {folder}" + (f" ({note})" if note else ""))


if __name__ == "__main__":
    main()
