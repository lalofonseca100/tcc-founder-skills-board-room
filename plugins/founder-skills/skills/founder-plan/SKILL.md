---
name: "founder-plan"
description: "Your business planner: compiles everything the founder skills wrote into one business plan with a computed verdict (Profitable, Not yet or Incomplete), a summary and a one-pager. Use for 'write my business plan'."
---

# founder-plan

The last step. One document a founder can act on, or hand to a partner or a
lender, built only from what the pack found.

The tool (where it lives is below):

```bash
python3 "$FOUNDER_TOOLS/founder-plan/compile.py" --dir founder
```

## Where the tools live

The Python tools are kept outside the skill. `$FOUNDER_TOOLS` below is the first
of these folders that holds them:

1. the `tools/` folder of this plugin (two levels above this skill's base directory)
2. `~/.claude/founder-tools`

If neither has them, download the reviewed version, pinned to one commit, and
check every script's SHA-256 before running anything:

```bash
FOUNDER_TOOLS=~/.claude/founder-tools
BASE=https://raw.githubusercontent.com/Jakeschincariol/founder-skill/fd9385b0cfe1b96bebce3898fbd506d73eff5a9d/skills
mkdir -p "$FOUNDER_TOOLS/founder-cfo" "$FOUNDER_TOOLS/founder-plan"
curl -fsSL "$BASE/founder-plan/compile.py" -o "$FOUNDER_TOOLS/founder-plan/compile.py"
curl -fsSL "$BASE/founder-cfo/unit_economics.py" -o "$FOUNDER_TOOLS/founder-cfo/unit_economics.py"
cd "$FOUNDER_TOOLS" && sha256sum -c - <<'SUMS'
1527c065d8258971cffd0dc9862aaf72fad18a64be69efc33b3ac817901098b7  founder-plan/compile.py
2df2cf18e87c992859f04bfb671827e76c4695b780023b56e75019c24a395ffc  founder-cfo/unit_economics.py
SUMS
```

If a check fails, stop and tell the user. Never run a script that fails it, and
never download from another commit or branch. The tools are standard-library
Python 3.8+ and never touch the network.

## Step 1: see what is there

```bash
python3 "$FOUNDER_TOOLS/founder-plan/compile.py" --dir founder --check
```

prints the verdict and each check. The checks, all computed:

1. Each unit earns money before fixed costs (`founder/numbers.json`).
2. Year 1 makes an operating profit.
3. The break-even fits inside capacity, if a capacity was given.
4. Enough simulated buyers buy (`founder/panel/results.json`; default bar 25%,
   change it with `--min-buy-rate` and say why).

**Multi-year businesses.** If `founder/plan.json` exists (the CFO's money plan),
use the multi-year compiler instead, everywhere below:

```bash
python3 -I "$FOUNDER_TOOLS/founder-plan/compile_multi.py" --dir founder --check
python3 -I "$FOUNDER_TOOLS/founder-plan/compile_multi.py" --dir founder
```

Its verdict comes from `founder-cfo/money_plan.py`: the bank balance never goes
below zero and the result is positive from the target year on. The buyer panel is
reported but not used as a check, because simulated buyers do not predict real
sales (and B2B buyers rarely say yes cold). It also adds the market
(`founder/market.md`) and the money plan (`founder/money-plan.md`) sections. Both
tools live in this plugin's `tools/` folder only
(`$FOUNDER_TOOLS/`; `compile_multi.py` SHA-256
`532e65e509aae9beb22f2b7503111edc1754fdfdc77ffda97efb1df88a2d8e52`); if they are
missing, say so and use `compile.py`.

If there are no numbers, the verdict is Incomplete: offer to run `/founder-cfo`.
List the other missing sections with the skill that fills each. Do not fill a
missing section yourself from guesses.

## Step 2: the summary

Write `founder/summary.md`, half a page, plain words:

- What the business is and who it is for, in two sentences.
- The verdict and the three numbers behind it (margin, break-even, year 1; for a
  money plan: the result per year, the lowest cash month and the cash needed).
- What the buyer panel and the board agreed on, and where they disagreed.
- The biggest risk and what will be done about it.
- What the founder needs to start (cash from the CFO, the first test from launch).
- The one thing to do this week.

If the verdict is Not yet, the summary leads with what has to change and which skill
changes it. Never soften a failing check.

## Step 3: compile

```bash
python3 "$FOUNDER_TOOLS/founder-plan/compile.py" --dir founder
```

writes `founder/business-plan.md`: title, the verdict and its checks, the key numbers
table, the idea, then every section the pack produced (summary, board, competition,
panel, pricing, offer, numbers, marketing, brand, operations, launch), and what is
not done yet.

## Step 4: the one-pager

Write `founder/one-pager.md` for someone deciding in two minutes: the problem, the
customer, the offer and price, the numbers table, the evidence (panel result,
competitor gap, any real test), what the money is for, and the ask. Same numbers as
the plan, word for word.

## Rules

- The verdict comes from `compile.py` or `compile_multi.py`. Never write Profitable by hand, and never
  round a failing number into a passing one.
- Say once, clearly: the panel is simulated buyers and the numbers are projections;
  real customers and real quotes confirm them. Not financial, legal or tax advice.
- If the user wants a PDF, a Word report or a deck, offer to export the plan, but
  keep the markdown as the source of truth and the same numbers word for word.

## Output

`founder/summary.md`, `founder/business-plan.md`, `founder/one-pager.md`. Then give
the user the verdict in one line and the one thing to do this week.

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
