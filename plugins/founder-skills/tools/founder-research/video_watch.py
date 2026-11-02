#!/usr/bin/env python3
"""video_watch.py - "watch" a video: key frames + captions on one timeline, for founder-research.

Captions alone miss what is on screen: slides, charts, numbers, code, product
demos, whiteboards. This tool picks the frames where the picture changes (scene
detection) plus one frame at least every --every seconds, removes near-duplicates,
and writes a timeline that puts each frame next to what was said at that moment.
Claude then looks at every frame (or the contact sheets first) and fills in
"On screen" notes, so the source card captures sound AND picture.

Run it where the video can be opened legally and without bypassing anything:
on the founder's own computer via Remote Control for YouTube (cloud servers get a bot
check), or anywhere for a local file the founder provides. The downloaded video is a
temporary working copy at <= 720p; it is always deleted at the end.

Needs: ffmpeg + ffprobe; yt-dlp only for URLs (pip install yt-dlp).
Usage:
  python3 -I video_watch.py --out founder/research/sources URL
  python3 -I video_watch.py --out founder/research/sources --captions talk.vtt talk.mp4
Options: --every 45 (max seconds without a frame), --scene 0.30 (0-1, lower = more
frames), --max-frames 150, --ytdlp "python3 -m yt_dlp", --lang en.
Output: <out>/<slug>/frames/f0001.jpg..., sheets/sheet01.jpg (3x3 overview),
frames.json, watch.md (timeline to annotate), meta.json, and a ledger.csv row.
"""
import argparse, csv, datetime, glob, hashlib, json, os, re, shlex, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from source_ingest import slugify  # noqa: E402  (same folder)

TODAY = datetime.date.today().isoformat()


def mmss(t):
    t = int(t); return f"{t // 3600:d}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60:02d}:{t % 60:02d}"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def fetch_video(url, ytdlp, lang, tmp):
    base = shlex.split(ytdlp)
    r = run(base + ["-J", "--skip-download", url], timeout=300)
    if r.returncode != 0:
        err = ([l for l in r.stderr.splitlines() if l.startswith("ERROR")] or r.stderr.splitlines()[-1:] or ["?"])[-1]
        if "not a bot" in err or "Sign in" in err:
            sys.exit("STOP: YouTube bot check. Do not bypass it (no cookies). Run this on the founder's computer, "
                     "or use a transcript the founder pastes.")
        sys.exit("FAILED: " + err[:300])
    info = json.loads(r.stdout)
    langs = f"{lang}.*,{lang},en.*,es.*"
    r = run(base + ["-f", "bv*[height<=720]+ba/b[height<=720]/b", "--merge-output-format", "mp4",
                    "--write-subs", "--write-auto-subs", "--sub-langs", langs, "--sub-format", "vtt",
                    "-o", os.path.join(tmp, "video.%(ext)s"), url], timeout=3600)
    vids = [f for f in glob.glob(os.path.join(tmp, "video.*")) if not f.endswith((".vtt", ".part"))]
    if r.returncode != 0 or not vids:
        sys.exit("FAILED download: " + (r.stderr.strip().splitlines() or ["?"])[-1][:300])
    subs = sorted(glob.glob(os.path.join(tmp, "video*.vtt")))
    human = info.get("subtitles") or {}
    cap_kind = "human" if any(k.startswith(lang) or k.startswith("en") for k in human) else ("auto" if subs else "none")
    up = info.get("upload_date") or ""
    meta = {"title": info.get("title"), "author": info.get("channel") or info.get("uploader"),
            "published": f"{up[:4]}-{up[4:6]}-{up[6:]}" if len(up) == 8 else None,
            "duration_min": round((info.get("duration") or 0) / 60, 1), "views": info.get("view_count"),
            "chapters": [{"start": mmss(c["start_time"]), "title": c.get("title")} for c in info.get("chapters") or []],
            "description": (info.get("description") or "")[:1500], "captions": cap_kind}
    return vids[0], (subs[0] if subs else None), meta


def duration(video):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video])
    try:
        return float(r.stdout.strip())
    except ValueError:
        sys.exit("FAILED: ffprobe could not read the video")


def extract(video, folder, scene, every):
    fdir = os.path.join(folder, "frames")
    shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    sel = f"select='eq(n\\,0)+gt(scene\\,{scene})*gte(t-prev_selected_t\\,2)+gte(t-prev_selected_t\\,{every})'"
    vf = f"{sel},showinfo,scale='min(1280\\,iw)':-2"
    r = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", video, "-vf", vf, "-fps_mode", "vfr", "-q:v", "3",
             os.path.join(fdir, "f%04d.jpg")], timeout=7200)
    times = [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    files = sorted(glob.glob(os.path.join(fdir, "f*.jpg")))
    if not files:
        sys.exit("FAILED: ffmpeg made no frames: " + r.stderr.strip()[-300:])
    return list(zip(files, times[:len(files)]))


def dedupe(frames, folder):
    """Drop frames that look almost the same as the last kept one (16x16 grey
    thumbnail, mean absolute difference), e.g. a speaker who did not move."""
    keep, last = [], None
    for f, t in frames:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vf", "scale=16:16,format=gray",
                              "-f", "rawvideo", "-"], capture_output=True).stdout
        if last is not None and len(raw) == len(last) and sum(abs(a - b) for a, b in zip(raw, last)) / len(raw) < 4:
            os.remove(f); continue
        keep.append((f, t)); last = raw
    # renumber so names stay in order
    out = []
    for i, (f, t) in enumerate(keep, 1):
        new = os.path.join(folder, "frames", f"f{i:04d}.jpg")
        if f != new:
            os.rename(f, new)
        out.append((new, t))
    return out


def thin(frames, max_frames):
    if len(frames) <= max_frames:
        return frames
    step = len(frames) / max_frames
    picked = {int(i * step) for i in range(max_frames)}
    for i, (f, _) in enumerate(frames):
        if i not in picked:
            os.remove(f)
    return [fr for i, fr in enumerate(frames) if i in picked]


def sheets(frames, folder):
    sdir = os.path.join(folder, "sheets"); shutil.rmtree(sdir, ignore_errors=True); os.makedirs(sdir)
    out = []
    for n in range(0, len(frames), 9):
        group = frames[n:n + 9]
        lst = os.path.join(sdir, "list.txt")
        with open(lst, "w") as fh:
            for f, _ in group:
                fh.write(f"file '{os.path.abspath(f)}'\nduration 1\n")
        name = os.path.join(sdir, f"sheet{n // 9 + 1:02d}.jpg")
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-vf",
             "scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2,tile=3x3",
             "-frames:v", "1", name])
        os.remove(lst)
        if os.path.exists(name):
            out.append((name, group[0][1], group[-1][1], [os.path.basename(f) for f, _ in group]))
    return out


def caption_cues(path):
    """[(start_seconds, text)] per caption cue; drops the rolling duplicate lines
    that auto-captions repeat and inline word timings."""
    if not path:
        return []
    cues, t, seen = [], None, set()
    for line in open(path, encoding="utf-8", errors="replace").read().splitlines():
        m = re.match(r"(?:(\d+):)?(\d\d):(\d\d)[.,]\d+\s+-->", line)
        if m:
            t = int(m.group(1) or 0) * 3600 + int(m.group(2)) * 60 + int(m.group(3)); continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if t is None or not line or line.isdigit() or line in seen:
            continue
        seen.add(line); cues.append((t, line))
        if len(seen) > 50:
            seen = set(list(seen)[-20:])
    return cues


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--captions", help="VTT/SRT file for a local video")
    ap.add_argument("--every", type=float, default=45)
    ap.add_argument("--scene", type=float, default=0.30)
    ap.add_argument("--max-frames", type=int, default=150)
    ap.add_argument("--ytdlp", default="yt-dlp")
    ap.add_argument("--lang", default="en")
    ap.add_argument("source")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    folder = os.path.join(a.out, slugify(a.source)); os.makedirs(folder, exist_ok=True)
    tmp = tempfile.mkdtemp()
    try:
        if os.path.exists(a.source):
            video, subs, method = a.source, a.captions, "local file + ffmpeg frames"
            meta = {"title": os.path.basename(a.source), "captions": "provided" if subs else "none"}
        else:
            video, subs, meta = fetch_video(a.source, a.ytdlp, a.lang, tmp)
            method = "yt-dlp (<=720p working copy) + ffmpeg frames"
        dur = duration(video)
        frames = thin(dedupe(extract(video, folder, a.scene, a.every), folder), a.max_frames)
        sh = sheets(frames, folder)
        cues = caption_cues(subs)
        if subs:
            shutil.copy(subs, os.path.join(folder, "captions.vtt"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rows = []
    for i, (f, t) in enumerate(frames):
        nxt = frames[i + 1][1] if i + 1 < len(frames) else dur + 1
        said = " ".join(txt for s, txt in cues if t - 1 <= s < nxt - 1)
        rows.append({"frame": os.path.relpath(f, folder), "t": round(t, 1), "time": mmss(t), "said": said,
                     "on_screen": ""})
    json.dump(rows, open(os.path.join(folder, "frames.json"), "w"), indent=2, ensure_ascii=False)

    words = sum(len(r["said"].split()) for r in rows)
    status = "opened" if cues and meta.get("captions") != "auto" else "partial"
    note = {"auto": "auto captions: names and numbers may be misheard", "none": "no captions: picture only",
            }.get(meta.get("captions"), "")
    meta.update({"source": a.source, "kind": "video", "method": method, "fetched": TODAY, "status": status,
                 "duration_min": meta.get("duration_min") or round(dur / 60, 1), "frames": len(rows),
                 "sheets": len(sh), "caption_words": words, "note": note})
    json.dump(meta, open(os.path.join(folder, "meta.json"), "w"), indent=2, ensure_ascii=False)

    with open(os.path.join(folder, "watch.md"), "w") as fh:
        fh.write(f"# {meta.get('title') or a.source}\n\nSource: {a.source}\nFetched: {TODAY} via {method}\n"
                 f"Duration: {meta['duration_min']} min · Frames: {len(rows)} · Captions: {meta.get('captions')}\n\n")
        if meta.get("chapters"):
            fh.write("Chapters: " + "; ".join(f"[{c['start']}] {c['title']}" for c in meta["chapters"]) + "\n\n")
        fh.write("Overview sheets (3x3, in order): " + ", ".join(
            f"{os.path.relpath(n, folder)} [{mmss(s)}-{mmss(e)}]" for n, s, e, _ in sh) + "\n\n")
        fh.write("How to annotate: open each sheet; for any frame with slides, charts, numbers, text, code, a demo\n"
                 "or a whiteboard, open the full frame and write what is on screen (exact numbers and labels).\n"
                 "Write 'speaker only' for talking heads. Never describe a frame you did not open.\n\n")
        for r in rows:
            fh.write(f"## [{r['time']}] {r['frame']}\n\nOn screen: TODO\n\nSaid: {r['said'] or '(no captions)'}\n\n")

    sha = hashlib.sha256(open(os.path.join(folder, "watch.md"), "rb").read()).hexdigest()
    ledger = os.path.join(a.out, "ledger.csv"); new = not os.path.exists(ledger)
    with open(ledger, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["date", "source", "kind", "method", "status", "sha256", "words", "folder", "note"])
        w.writerow([TODAY, a.source, "video", method, status, sha, words, folder, f"{len(rows)} frames; {note}"])
    print(f"{status.upper()} {a.source}: {meta['duration_min']} min, {len(rows)} frames, {len(sh)} sheets, "
          f"{words} caption words -> {folder}/watch.md")


if __name__ == "__main__":
    main()
