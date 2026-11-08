---
name: "founder-pricing"
description: "Finds the price buyers will pay: a Van Westendorp range from the panel's price answers, set against competitor prices and the CFO's margin, with a price, a ladder and an opening offer to test. Use for 'how much should I charge'."
---

# founder-pricing

Price is the fastest lever on the margin and the one founders guess most. This
skill sets it from three things you can check: what buyers said, what competitors
charge, and what the business needs to earn.

The tool (where it lives is below):

```bash
python3 "$FOUNDER_TOOLS/founder-pricing/van_westendorp.py" founder/panel/answers --price 6.50 --out founder/pricing-curve.md
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
mkdir -p "$FOUNDER_TOOLS/founder-cfo" "$FOUNDER_TOOLS/founder-pricing"
curl -fsSL "$BASE/founder-pricing/van_westendorp.py" -o "$FOUNDER_TOOLS/founder-pricing/van_westendorp.py"
curl -fsSL "$BASE/founder-cfo/unit_economics.py" -o "$FOUNDER_TOOLS/founder-cfo/unit_economics.py"
cd "$FOUNDER_TOOLS" && sha256sum -c - <<'SUMS'
5915a505a8e54c479eaba12009ba988e38926c14e00adbbf9f37b61e5b112870  founder-pricing/van_westendorp.py
2df2cf18e87c992859f04bfb671827e76c4695b780023b56e75019c24a395ffc  founder-cfo/unit_economics.py
SUMS
```

If a check fails, stop and tell the user. Never run a script that fails it, and
never download from another commit or branch. The tools are standard-library
Python 3.8+ and never touch the network.

## Step 1: what buyers said

If `/founder-consumer` ran, every buyer answered four price questions. Run the
tool on `founder/panel/answers` (or a CSV with the columns `too_cheap, cheap,
expensive, too_expensive` from real surveys, which beat simulated answers every
time). It reports:

| point | meaning |
| --- | --- |
| PMC | below this, too many think it is too cheap to be good |
| OPP | the price with the least resistance either way |
| IPP | where as many call it a bargain as call it expensive |
| PME | above this, too many will not buy at all |

PMC to PME is the acceptable range. If the panel has not run, say so and offer to
run `/founder-consumer --quick` first. Do not invent a range.

## Step 2: what competitors charge

From `founder/competitors.md` (or look them up now, from their own public price
pages, with links): the price of the nearest substitutes for the same job. Note
what each price includes, so you compare like with like. A matcha latte is
compared with other matcha lattes and with the coffee it replaces, not with a tea
bag.

## Step 3: what the business needs

From `founder/numbers.json`: the variable cost per unit and the break-even. Run the
CFO's tool at two or three candidate prices to see the margin and break-even at
each:

```bash
python3 "$FOUNDER_TOOLS/founder-cfo/unit_economics.py" founder/numbers.json --price 7.00
```

## Step 4: decide

Write `founder/pricing.md`:

1. **The price**, and why: where it sits in the acceptable range, against the
   competitors, and the margin it gives (from the tool, not a guess).
2. **The ladder**, if the business can have one: a good / better / best (size,
   bundle, subscription, membership) with a reason to step up each rung.
3. **The opening offer**: an intro price or bonus for launch that does not train
   buyers to wait for discounts, with an end date.
4. **What to test with real buyers**: two prices inside the range and how to test
   them (two landing pages, a pre-sale at each, A/B on the menu board).
5. The panel's verbatim price objections (top three), so marketing can answer them.

## Rules

- Price answers from simulated buyers pick what to test. They are not proof.
- Never price below variable cost to "buy" customers without saying so, and how
  long the CFO says the business can afford it.
- No fake anchors: no "was $X" price that was never charged.

## Output

`founder/pricing.md`, `founder/pricing-curve.md`. If the price changed, update
`founder/numbers.json` and re-run `/founder-cfo`. Next: `/founder-offer`.

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
