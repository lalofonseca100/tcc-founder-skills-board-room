# founder-research: reference

Detail moved out of SKILL.md to save tokens. Read only the part the task needs.

## Step 2: open each source (never invent)

Web pages: The founder-cto research ladder (WebSearch, web-fetch agent,
`polite_fetch.py`, `render_fetch.js`, other doors, the founder's browser). Other kinds:
`source_ingest.py` (default `$FOUNDER_TOOLS` = `$FOUNDER_TOOLS/`):

```
python3 -I $FOUNDER_TOOLS/founder-research/source_ingest.py --out founder/research/sources URL_OR_FILE ...
```

It saves captions, PDFs, arXiv papers with official metadata, and
files the founder uploads, each with date, method, SHA-256 and a status: `opened`,
`partial` (auto captions, abstract only, under 300 words) or `failed` with the
reason.

**YouTube ladder** (YouTube shows a bot check to cloud servers; tested
2026-11-01, so rung 2 often fails here):
1. An official transcript or show notes on the creator's site, podcast page or
   newsletter (many interviews publish one).
2. `source_ingest.py` captions with yt-dlp (`--ytdlp "python3 -m yt_dlp"`).
3. web-fetch agent on the video page: title, date, description and chapters
   only. That is metadata, not the content: the card stays `partial`.
4. The founder pastes the transcript (YouTube: "...more" > "Show transcript") or uploads
   notes; ingest the file.
5. `video_watch.py` on the founder's own computer via Remote Control (next section).

Never pass cookies, log in as the founder or solve a bot check.

**Watching a video (sound and picture).** Captions miss what is on screen:
slides, charts, numbers, code, demos, whiteboards. For any talk, masterclass or
interview where the picture may carry information, use `video_watch.py`:

```
python3 -I $FOUNDER_TOOLS/founder-research/video_watch.py --out founder/research/sources URL
```

It takes a temporary working copy (720p at most), picks the frames where the
picture changes plus one at least every 45 s, drops near-duplicates, makes 3x3
overview sheets, and writes `watch.md`: each frame next to what was said at that
moment. Then look at every sheet; open each full frame that shows slides, charts,
numbers, text, code or a demo, and fill in "On screen" with exact labels and
numbers ("speaker only" for talking heads). The video copy is deleted at the end.
A frame you did not open gets no description.

YouTube blocks cloud servers, so videos run on the founder's computer via Remote Control,
with the founder's OK each session (it needs ffmpeg and yt-dlp there). During a cloud run,
add such videos to `video-queue.md` and work from captions or transcripts until
the queue is processed; mark those cards `partial (no picture yet)`. The session on
the founder's computer annotates the frames there and sends back the finished `watch.md`
and `meta.json` (text) for the card; the frames stay on that computer unless the founder
asks for them.

**Online courses** (for example Coursera): use the transcripts and slides the
platform lets the founder download, or the founder's notes. No automated login.

**Papers behind a paywall**: look for the legal open copy (arXiv, the author's
page, the OpenAlex or Semantic Scholar record's open-access link). **Books and
paid courses**: only the publisher's preview, the author's free material, or notes
and exports the founder owns. Never pirate sites.

If no rung opens a source: write its card with status `not opened`, list what
was tried, and make no claim about its content. A title, a thumbnail or a summary
by someone else is not the source.

