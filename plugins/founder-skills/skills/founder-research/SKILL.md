---
name: founder-research
description: Your R&D department: finds and reads the best sources (YouTube talks, interviews, papers, masterclasses, book summaries, web pages), grades their quality, distills insights and proposes upgrades to the other founder skills. Use for 'research X in depth', 'analyse this video/paper/book' or the R&D run.
---

# founder-research

An R&D department turns the outside world's best knowledge into better ways of
working. This skill does three jobs: **reads** a source honestly (or says it
could not), **grades** how far it can be trusted, and **turns** what survives
into a tested change to how the founder skills work. It is how the company
becomes an AI-first company that keeps learning in the directions the founder sets and in
the ones the evidence says pay off most.

v1.0 (2026-11-02). It builds on two skills and does not repeat them:
`founder-cto` owns the research ladder and the web fetch tools; `founder-learning`
owns watchlists, the changelog and the founder's approval of every skill change.

## Files

All in `founder/research/` (in this project `founder/research/`):

- `agenda.md`: the research directions. Each line: direction | why it matters
  (project, money or goal) | set by (the founder / R&D proposal) | priority 1-3 | cadence
  | status (active, proposed, paused). Only the founder adds or activates a direction.
- `sources/`: dated text copies, one folder per source (`text.md`, `meta.json`) and
  `ledger.csv`, written by `source_ingest.py` or founder-cto's fetch tools.
- `cards/<slug>.md`: one source card per source (format in Step 3).
- `insights.md`: the insight register (format in Step 5).
- `video-queue.md`: videos waiting to be watched on the founder's computer (URL | why |
  direction | added date | status).
- `digest-YYYY-MM-DD.md`: the output of each run or deep dive.

## The method

Recognised methods, in our own words:

- **SIFT** (Mike Caulfield, 2019): Stop; Investigate the source; Find better
  coverage; Trace claims to the original. Used before reading anything closely.
- **Admiralty code** (NATO AJP-2.1 source grading): source reliability A
  (reliable) to F (cannot judge) x information credibility 1 (confirmed by other
  sources) to 6 (cannot judge). Every card gets a grade such as B2.
- **Evidence ladder** (evidence-based medicine, adapted for business): systematic
  review or meta-analysis > controlled experiment > large dataset or survey with
  method shown > case study > expert opinion or anecdote. An interview guest's
  story is one case (n=1) unless they show data.
- **Triangulation**: an insight becomes "supported" only with two independent
  sources, or one primary source graded A1-B2. Otherwise it is a "hypothesis" to
  test, not a rule.
- **Double-loop learning** (Argyris and Schön, *Organizational Learning*, 1978):
  ask not only "how do we do this better" but "is our assumption right". Every
  insight names which assumption in a skill it confirms or breaks.

Watch for the usual traps: survivorship bias (founders who won tell the story),
selling bias (the source sells a course, tool or book), recency hype, and
summaries of summaries.

## Step 0: the brief

Which mode?

- **Deep dive**: a question ("best way to price agency retainers", "how AI-first
  companies run ops"). Write the question, the decision it serves, the project, the
  deadline, and what "done" looks like (for example 8-15 graded sources).
- **Source analysis**: The founder shares a link or file. Same steps, one source.
- **R&D run**: on cadence or on request. Read `agenda.md`; take the active
  directions that are due, highest priority first.

Ask the founder only what blocks the work.

## Step 1: find sources

Search wide, then pick the best. For each direction or question, run several
WebSearches in one turn (English first, then Spanish and Dutch when relevant):
"<topic> research", "<topic> meta-analysis", "<topic> case study", "<expert>
interview", "<book> summary", "<topic> site:youtube.com". Then look for:

- **Primary research**: papers (arXiv, SSRN, Google Scholar, OpenAlex API,
  Semantic Scholar API), official statistics, company filings, datasets.
- **Practitioners with skin in the game**: operators who show numbers (engineering
  blogs, founder letters, conference talks, long interviews).
- **Teaching material**: masterclasses, university lectures (MIT OpenCourseWare,
  Stanford, YC Startup School), book summaries. Use a summary to find the idea,
  then trace it to the book, the author's own talks or articles.

Prefer fewer, better sources. Note sources you rejected and why (one line each).

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

## Step 3: the source card

`cards/<slug>.md`, in English:

```
# <title>
Source: <URL> · Type: <video/interview/paper/course/book summary/page>
Author: <who> · Published: <date> · Opened: <date> via <method> · Status: <opened/partial/not opened>
Grade: <A-F><1-6> because <one line: track record, method, conflicts of interest>
Evidence level: <meta-analysis ... anecdote>
Selling something? <yes/no, what>

## Key claims (max 7)
1. <claim, in our words> · where: <[mm:ss] or p. N> · backed by: <data / study / story>

## New for us
- <what our skills do not already know or do; name the skill and section>

## Doubts
- <what is weak, missing, or contradicted elsewhere>
```

Quote at most a sentence or two at a time; paraphrase the rest. Do not copy
whole transcripts or chapters into cards or reports (they stay in `sources/`,
inside the project).

## Step 4: synthesise

Across the cards for a question or direction:

1. Group claims that agree; mark where good sources disagree and why (different
   market, size, year, method).
2. Weigh by grade and evidence level, not by how often a claim is repeated.
3. Write each candidate insight: what it says, which sources back it (card links),
   status (`supported` / `hypothesis`), and what it would change.
4. Be critical: list what would make the insight false and the cheapest way to
   test it in our work (a pilot, an A/B test, one client project).

## Step 5: integrate into our frameworks

Append to `insights.md`:

```
## <YYYY-MM-DD> · <insight in one line>
- Status: supported | hypothesis · Sources: <card links> · Grade: <best grades>
- Assumption it tests: <skill + section + current rule>
- Proposed change: <exact edit to which skill, file or tool>
- Test: <how we will know it works> · Projects affected: <list>
- Approval: pending
```

Then hand every proposed skill change to `founder-learning` as a **method
change** entry in its changelog (its format, with this insight as the source).
founder-learning asks the founder and, after a yes, proposes the updated skill. This
skill never edits a skill file itself and never proposes a skill update directly.

Only `supported` insights may change a skill's rules. A `hypothesis` may add a
test or an option, marked as such.

## Step 6: report to the founder

Write `digest-YYYY-MM-DD.md` in the founder's house format (a `working-with-<founder>` skill, if one exists): 1. How this
was made (searches, sources found, opened, rejected, not opened). 2. The answer
or the top insights in three sentences. 3. Insights table (insight, status,
grade, skill affected). 4. Proposed changes and tests. 5. What we could not open
or verify. 6. Source list with dates and grades.

Weekly R&D brief (Monday morning): keep the digest to one page, a five-minute
read: the top three insights, what to try this week, approvals waiting, and the
video queue. Deep dives can be longer.

Then one short message in Spanish: the two or three insights that matter most
(money or time impact first), the changes waiting for approval, and the sources
not opened. Attach the digest.

## The research agenda (continuous learning)

The agenda is how R&D learns "in the line the founder sets and the one that suits us
most". Two kinds of direction:

- **Set by the founder**: added as given; R&D only refines the wording and cadence.
- **Proposed by R&D**: at most two per run, each with the evidence for it, scored
  as impact on a live project or goal (1-3) x strength of evidence (1-3) x cost to
  learn (3 = cheap). Shown to the founder with the score; it becomes active only after
  the founder's yes.

Each run also checks the active directions: anything learned that changes a
priority, and directions with no useful insight in three runs are proposed for
pause. Keep at most seven active directions.

## Keeping current (ever-learning)

The R&D run itself has its own weekly scheduled task (Monday morning, so the brief
is ready when the founder starts the week). The tools it depends on follow
`founder-learning`: watchlist `founder/learning/watchlists/founder-research.md`,
cadence weekly (yt-dlp releases, YouTube access from cloud servers, arXiv,
OpenAlex and Semantic Scholar APIs, the grading methods).

## Rules

- Never invent what a source says. Not opened means no claims, marked `not opened`.
- Video copies are temporary working files on the founder's computer only: never kept,
  shared or uploaded.
- Every claim in a card points to a place in the source (timestamp, page, section).
- Grade every source; say who pays the author and what they sell.
- The founder approves every agenda change and every skill change.
- Private by default: cards, digests and the agenda stay in the project. No
  personal details about the founder or clients in search queries, external tools or
  anything that leaves the project.
- Respect copyright and terms: no piracy, no paywall or bot bypass, short quotes only.
- Plain Spanish in messages to the founder, English in the files.
