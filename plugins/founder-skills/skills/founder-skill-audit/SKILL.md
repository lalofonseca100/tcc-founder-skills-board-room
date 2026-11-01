---
name: founder-skill-audit
description: Audits the founder skills (or any skill set) for validity and strength, scores each one, finds missing skills for the company's projects and drafts what to add. Use for 'audit our skills' or 'what skills are we missing'.
---

# founder-skill-audit

A skill is only as good as the decisions it supports. This audit checks each
founder skill against a fixed scorecard, looks at how it actually performed on
real projects, and finds the jobs no skill covers yet. It ends with a ranked list
of fixes and new skills, ready to build.

## Step 0: collect the evidence

Read, do not skim:

1. **The skills.** Every installed `founder-*` SKILL.md (in this project the synced
   copies under `~/.claude/skills/synced/*/`, or this plugin's `skills/` folder).
   Note each one's inputs (files it reads), outputs (files it writes) and method.
2. **The tools.** `$FOUNDER_TOOLS` (default: the `tools/` folder of this plugin):
   what each script can and cannot model (units, time horizon, currency, checks).
3. **Use evidence.** Past runs in `founder/` (outputs, reports, `doc-review.md`) and
   project memory. The strongest signal is **workaround work**: chapters, files or
   spreadsheets someone had to make outside the pack (for example `founder/v2/*.md`
   with no skill behind it). Also note outputs the founder rejected or overrode.
4. **The portfolio.** The projects the skills must serve: the company's
   projects (a projects list such as `founder/projects.csv`, and memory) and their
   type (B2B service, agency, software, consumer, non-profit).
5. **House rules.** The founder's `working-with-<founder>` skill, if any: sources, methodology first,
   plain English, every number derived.

Write one line per piece of evidence with its file path, so every finding can cite
it ("according to `founder/v2/money.md` ...").

## Step 1: score every skill

Nine criteria, each scored 0 to 3 (0 = missing, 1 = weak, 2 = adequate,
3 = strong). Give one sentence of evidence per score, with a file path or line.

| # | criterion | the question | a 3 looks like |
| --- | --- | --- | --- |
| 1 | Method validity | Is the method a recognised one, applied correctly, with its limits stated? | Named, well-tested method (unit economics, lean pilot tests); limits written in the skill |
| 2 | Evidence | Does it force real sources and keep facts apart from estimates? | Every fact linked; estimates marked; real data preferred to simulated |
| 3 | Traceability | Can each number or score be rebuilt by someone else? | Computed by a tool, or derivation shown; scores have an anchored rubric |
| 4 | Fit to our projects | Does it work for our project types, market and currency (B2B services, agencies, software, NL/EU, EUR, multi-year)? | Works without workarounds for every active project type |
| 5 | Hand-offs | Do the files it reads exist when it runs, and does the next skill use what it writes? | No dead inputs; outputs consumed downstream |
| 6 | Guardrails | Does it stop fake data, overclaiming and advice it cannot give? | Explicit rules, legal and financial limits stated once |
| 7 | Decision value | Does it end in a clear decision, a number and a next step, in the founder's format? | Verdict + next action; usable in the docx/deck without rewriting |
| 8 | Proven in use | Did it hold up on real projects? | Used as-is; no rework; the founder kept the result |
| 9 | Freshness | Are its sources dated and checked on time? | Has a watchlist in `founder/learning/watchlists/`; checked within its cadence in `last-run.md`; no `unverified` value used as fact; approved changes applied |

**Strength** = the total out of 27: **Strong** 23+, **Solid** 18-22, **Weak**
14-17, **Rebuild** 13 or less. (Audits before 2026-11 used 8 criteria out of 24;
to compare, look at criteria 1-8.)

**Validity flag**: a 0 on criterion 1 or 2 makes the skill "not valid until fixed"
whatever its total, because its conclusions cannot be trusted.

Score the skill as written and as it behaved, never as it could be. Do not round
up; a 1 is a result. If you have no use evidence for criterion 8, score it 1 and
say "not yet tested".

## Step 2: find the gaps

Three passes. A gap counts only if at least one pass gives evidence for it.

1. **Lifecycle coverage.** Map the skills onto the founder jobs below and mark each
   covered, partly covered or missing:
   idea test · market size and trends · competitors · real customer discovery ·
   simulated buyers · pricing · offer · multi-year money plan and cash flow ·
   funding (grants, loans, investors) · legal set-up, contracts, IP, privacy ·
   tax and VAT · brand · marketing · B2B sales and pipeline · operations ·
   team, roles, partner agreements, hiring · launch · metrics after launch ·
   expansion to new countries · running a portfolio of projects · business plan.
2. **Workarounds.** Every file from Step 0.3 made outside a skill is a candidate
   gap. Name the file and what it did.
3. **Broken promises.** Places where a skill points to another skill for something
   that skill does not do (for example a skill saying "market size comes from
   `/founder-competitors`" when that skill never sizes a market).

Rank each gap: **Need** (how many active projects need it: 0-3) × **Cost of being
wrong** (1 low, 2 money lost, 3 legal or cash crisis) × **Evidence** (1 one pass,
2 two or more). Highest first. Say whether the gap is best closed by a **new
skill** or by an **improvement** to an existing one: prefer improving when the job
fits an existing skill's method and files.

## Step 3: draft the fixes

For the top three to five items, write a one-screen brief:

- **Name and trigger**: `founder-<job>`, and the one-sentence description.
- **Job**: the decision it supports and who uses it.
- **Method and source**: a recognised method, cited (book, official guide,
  regulator page). No method, no skill.
- **Inputs and outputs**: which `founder/` files it reads and writes, and where it
  sits in the pack's order (`board -> competitors -> ... -> plan`).
- **Guardrails**: what it must never do (invent figures, give legal advice...).
- **Test**: how we will know it works: re-run it on a past project and compare with
  the workaround file it replaces.

## Step 4: report

Write `founder/audit/skill-audit-<YYYY-MM-DD>.md` and
`founder/audit/scorecard-<YYYY-MM-DD>.csv`
(`skill,c1..c9,total,band,valid,main_issue`). The report, in the founder's format:

1. **How this audit was made** (this method in five lines, the evidence list).
2. **Headline**: the overall pattern in three sentences.
3. **Scorecard** table with one main issue per skill.
4. **Gaps**, ranked, each with its evidence.
5. **Recommended next builds**: the briefs from Step 3.
6. **What this audit cannot see** (skills never run, tools not tested).

Give the founder the headline and the top three builds in the chat, link the report.

## Step 5: build only what the founder approves

Ask the founder which briefs to build (a decision card works). For each approved one,
write the full SKILL.md (with the `skill-creator` skill if available) and offer it
with `propose_skills`: kind `new` for a new skill; kind `improvement` with the
complete updated SKILL.md for an existing one. At most three per batch; if the
tool says rate limited, wait about an hour. Never edit the skill files on disk.
Then re-run Step 1 on the changed skills and record the new scores in the next
audit.

## Rules

- Every score and every gap cites a file, a line or a run. No evidence, no finding.
- Audit the skill, not the business it was used on.
- Keep the honest limits each skill already states; do not score a skill down for
  saying what it cannot do.
- Plain English, concise. Not legal, tax or financial advice.

## When to run it

After every full pack run on a new project, when a new project type joins the
portfolio, after a `founder-learning` run that changed a method, or when the founder asks.
For criterion 9, read `founder/learning/last-run.md` and the latest
`changelog-*.md`; a skill with no watchlist scores 0 on freshness. Compare with the last audit in `founder/audit/`.
