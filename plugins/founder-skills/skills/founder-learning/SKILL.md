---
name: founder-learning
description: Keeps every founder skill current: re-reads each skill's watchlist when it is due, logs what changed in the world with dated sources, and drafts skill updates for the founder to approve. Use for 'refresh the skills', 'what changed', the weekly learning run, or when a source looks out of date.
---

# founder-learning

Skills go stale: prices move, laws change, new AI models ship. This skill is the
pack's memory for the outside world. It checks what each skill depends on, writes
down what changed with a source and a date, and proposes updates. It never changes
a skill on its own: The founder approves every change.

## Schedule

The learning run and the R&D run (`founder-research`) are one combined
scheduled run every two weeks (1st and 15th of the month). Do learning first,
then R&D, then leave one CoS inbox entry for both. Use small models for the
mechanical checks (see Token budget).

## Files

All in `founder/learning/`:

- `watchlists/<skill>.md`: what to watch, where, why, and a **cadence** (weekly,
  monthly, quarterly, yearly, or event-driven). One per skill.
- `last-run.md`: table `skill | cadence | last checked`.
- `changelog-YYYY-MM.md`: one entry per change found (format below).

First run: if `founder/learning/` does not exist, copy the starter watchlists from
this plugin's `templates/learning/watchlists/` and create `last-run.md` with every
list at "never". A new skill gets a watchlist the day it is added (ask its author thread or write
it from the skill's own sources).

## Step 1: what is due

Read `last-run.md`. A watchlist is due when its cadence has passed since its last
check (weekly 7 days, monthly 30, quarterly 91, yearly 365; "never" is due).
Event-driven ones are due when their event happened (for example `founder-plan`
after any approved change to cfo, market or tax). Also due: any skill the founder names.

## Step 2: check each due item

For every line of a due watchlist, open the source using the research ladder in
`founder-cto` (WebSearch, web-fetch, `polite_fetch.py`, `render_fetch.js`, other
doors such as API, sitemap, PDF or Wayback Machine). Compare with what the skill
and its files assume today (its SKILL.md, its tool's JSON, `sources.md`).

Classify each finding:

- **No change**: note nothing except the check date.
- **Data change** (a price, rate, threshold or date in a file such as
  `rules.json`, `stack.md`, `competitors.csv`): the value, old and new.
- **Method change** (a law, framework, tool or best practice that changes how the
  skill works).
- **Could not check**: which rung failed and why (network, robots.txt, login).

Status words, borrowed from founder-tax: `law` / `official` (in force or
published by the owner), `proposal` (announced, not final), `unverified` (one
non-official source). Only `law`/`official` facts may replace a value.

## Step 3: write the changelog

Append to `changelog-YYYY-MM.md`, newest first:

```
## YYYY-MM-DD · <skill> · <data | method | could not check>
- What changed: <old> -> <new> (status)
- Source: <URL>, published <date>, checked <date>
- Effect: <which file, number or step, and which projects (each affected project)>
- Proposed: <the exact edit> · Approval: pending
```

Then update `last-run.md` with today's date for every watchlist you checked.

## Step 4: tell the founder and get approval

One short message in Spanish: how many lists were checked, the changes that matter
(money or legal impact first), and what could not be checked. Ask the founder to approve
or reject each proposed change (a decision card for one big change; numbered
questions for several).

Only after approval:
- **Data change** in a project file or tool JSON: edit the file, mark the
  changelog entry `Approval: yes (date)`, and say which past reports may now be out
  of date (do not rewrite them unless asked).
- **Method change** in a SKILL.md: propose the complete updated skill with
  `propose_skills` (kind `improvement`, at most three per batch). Never edit skill
  files on disk.

## Step 5: improve the watchlists

When a check finds a better source, a dead link, or a recurring surprise, propose
adding it to the watchlist in the same message. Watchlist edits are data, so they
also need the founder's OK.

## Rules

- Every change has a source URL and two dates. No source, no change.
- Report "could not check" honestly; never fill gaps with memory.
- Do only what the watchlists and the founder ask; do not rewrite reports or skills unasked.
- Plain Spanish in the message, English in the files. Not legal or tax advice.

## Token budget (always)

Tokens are the pack's running cost. Every skill follows these rules unless the
founder asks for more:

- **Start lite.** Give the smallest output that settles the question (a verdict,
  a table, one page). Build the full report, deck or Word file only when the
  founder asks for it, and only for the final version.
- **Read only what the task needs.** Search before reading, read big files in
  parts, never re-read a file already in the conversation, skip images unless the
  picture matters.
- **Right model for the job.** Mechanical steps (copying data, syncing, checking
  links, formatting) go to a sub-agent on `haiku`; drafting on `sonnet`; keep the
  strongest model for judgement and decisions.
- **Swarms start small.** Panels and boards run their quick size first; say the
  estimated cost before a full run.
- **No new recurring task** (scheduled run, sync, watcher) without the founder's
  OK and a cost-per-week estimate. Prefer on-demand runs.
- **Short threads.** One task per thread; when a thread grows long (about 200k
  tokens of context), write a one-page handoff and continue in a fresh thread.
- **Edit, don't rebuild.** Change a file or page with small edits instead of
  rewriting and republishing it whole.
