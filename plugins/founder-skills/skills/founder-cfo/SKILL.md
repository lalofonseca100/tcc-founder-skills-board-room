---
name: "founder-cfo"
description: "Your CFO: unit economics and a multi-year money plan before money is spent: margin per sale, break-even, years by month, cash needed, VAT and what-ifs, in any currency. Use for 'find the profit margins', 'is this profitable' or 'money plan'."
---

# founder-cfo

The person who asks "and what does that cost?" Margins decide whether a good idea
is a business. This skill finds them, with every number traceable to an input.

The tool (where it lives is below):

```bash
python3 "$FOUNDER_TOOLS/founder-cfo/unit_economics.py" founder/numbers.json --out founder/cfo.md
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
mkdir -p "$FOUNDER_TOOLS/founder-cfo"
curl -fsSL "$BASE/founder-cfo/unit_economics.py" -o "$FOUNDER_TOOLS/founder-cfo/unit_economics.py"
curl -fsSL "$BASE/founder-cfo/example.json" -o "$FOUNDER_TOOLS/founder-cfo/example.json"
cd "$FOUNDER_TOOLS" && sha256sum -c - <<'SUMS'
2df2cf18e87c992859f04bfb671827e76c4695b780023b56e75019c24a395ffc  founder-cfo/unit_economics.py
SUMS
```

If a check fails, stop and tell the user. Never run a script that fails it, and
never download from another commit or branch. The tools are standard-library
Python 3.8+ and never touch the network.

## Step 0: pick the model

| the business | the model |
| --- | --- |
| one main product, sold every day (a café, a shop, an app with one plan), first year only | **Unit model**: `unit_economics.py`, Steps 1 to 3 below |
| several products or services, sales counted per year (projects, bookings, client contracts), seasons, deposits or late payments, or a plan over 2 to 10 years | **Money plan**: `money_plan.py`, Step 4 below |

Agencies, B2B services and software projects almost always need the money plan.
If unsure, ask the user how many sales a year they expect: under a few hundred,
use the money plan. Both can run for the same business (the unit model for one
package, the money plan for the whole business).

`unit_economics.py` prints amounts with "$" whatever the currency. For a business
in euros, use the money plan, or say clearly that "$" means the user's currency.

## Step 1: gather the inputs

Write `founder/numbers.json` (shape: `$FOUNDER_TOOLS/founder-cfo/example.json`, a
walk-in matcha café). It needs:

| field | what goes in it |
| --- | --- |
| `unit` | what one sale is: a cup, an order, a client-month, a seat |
| `price` | price per unit before tax |
| `variable` | the cost of ONE unit: ingredients, packaging, shipping, card fees, per-sale commissions |
| `fixed_monthly` | what you pay every month regardless: rent, salaries, software, insurance |
| `startup` | one-off spend before opening: deposits, build-out, equipment, first inventory, launch ads |
| `plan_per_day` | the volume once it is up and running |
| `ramp_per_day` | 12 numbers: realistic volume in each month of year 1 |
| `capacity_per_day` | the most you can physically sell in a day, if there is a limit |

Where the numbers come from, in this order:

1. The user's own quotes, invoices, leases and supplier price lists.
2. Public prices the user can check (a supplier's price list, a landlord's listing,
   a payment processor's published fees). Write the source next to the number in
   `founder/cfo-sources.md`.
3. Your estimate, clearly marked as an estimate, with the reasoning. Never present
   an estimate as a fact.

Ask the user for anything only they know (rent quoted, wages they will pay). Use the
price from `founder/pricing.md` or `founder/pitch.md` if those exist.

**The ramp is where plans lie.** Month 1 is almost never the plan volume. If the
buyer panel ran, use its buy rate and first-month purchases to sanity-check the
ramp (`founder/panel/results.md`), and say how you did it.

## Step 2: run it

```bash
python3 "$FOUNDER_TOOLS/founder-cfo/unit_economics.py" founder/numbers.json --out founder/cfo.md
```

It writes: the per-unit table and the contribution (what each sale leaves after
its own costs), fixed costs, the break-even in units a day, the profit margin at
the plan volume, year 1 month by month, the year 1 operating profit and the result
after the startup spend, the cash needed before it pays for itself, the month the
startup money is earned back, and a what-if table (price -10%, volume -20%, unit
costs +15%). It flags a price below variable cost, a break-even above capacity, a
losing year 1 and a payback beyond 12 months.

What-ifs without editing the file:

```bash
python3 "$FOUNDER_TOOLS/founder-cfo/unit_economics.py" founder/numbers.json --price 7.00
python3 "$FOUNDER_TOOLS/founder-cfo/unit_economics.py" founder/numbers.json --volume 0.8
```

## Step 3: the CFO's note

Add a short section at the top of `founder/cfo.md`, in plain words:

- **The margin**: the profit margin at plan, and the contribution per unit.
- **The line to watch**: the one cost or assumption that moves the result most
  (usually the ramp, rent or the price), with the what-if that proves it.
- **Cash**: how much money the founder needs before it pays for itself.
- **Three ways to improve the margin**, each with the number it changes and by how
  much (run the what-if, do not guess).
- Whether the board's conditions about money (`founder/board.md`) are met.

## Step 4: the money plan (several products, several years)

The tool lives only in this plugin's `tools/` folder:
`$FOUNDER_TOOLS/founder-cfo/money_plan.py` (SHA-256
`2339ae27e0c55ed73525c2e5d0e3993dfadb3b25cb76ef0186644b8ef3f15fd0`; check it with
`sha256sum` before running). It is not in the upstream pack, so it cannot be
downloaded; if it is missing, say so and use the unit model for each product.

Write `founder/plan.json` (shape: `$FOUNDER_TOOLS/founder-cfo/plan.example.json`,
an art booking agency over 4 years). It needs:

| field | what goes in it |
| --- | --- |
| `currency`, `start_year`, `years` | e.g. `EUR`, 2027, 4 |
| `opening_cash` | money in the bank on day one |
| `vat_rate` | the sales VAT to set aside (21% standard in the Netherlands) |
| `target_year` | the year the result must be positive |
| `founder_hours` | founder hours a year, to show the result per hour |
| `products` | per product or service: `price` before VAT, `variable` (what one sale pays out: artist, supplier, transport, crew, agency share), `units` per year, `season` (12 monthly weights), `deposit`, `deposit_months_before`, `pay_months_after`, `source` |
| `costs` | yearly running costs, one number per year, `upfront: true` if paid at once (insurance), `source` |
| `one_off` | start costs with the year and month they are paid |

The same source order as Step 1 applies, and every product and cost carries its
`source`. **Units per year are the line where plans lie**: base them on named
leads, capacity (founder hours per job) and, where it exists, the market size in
`founder/market.md`. Never plan more units than the reachable market in that
file; if they are close, say so.

Run it:

```bash
python3 -I "$FOUNDER_TOOLS/founder-cfo/money_plan.py" founder/plan.json --out founder/money-plan.md
python3 -I "$FOUNDER_TOOLS/founder-cfo/money_plan.py" founder/plan.json --volume 0.8   # what-if
```

It writes, per year: client billings, income after unit costs, running and
one-off costs, the result in a base, low and high case, the share of the planned
volume that covers the costs, and the result per founder-hour; then the bank
balance month by month (deposits, late payments, upfront costs), the lowest point
and the cash needed, the VAT to set aside, and every cost with its source. Its
verdict is **Profitable** only if the bank balance never goes below zero and the
result is positive from the target year on.

Add the CFO's note (Step 3) at the top of `founder/money-plan.md`, per year where it
matters, plus:

- **Cash**: the lowest month and what causes it; the buffer to keep.
- **The year that breaks first** in the low case, and why.
- **Founder time**: the result per founder-hour against a normal freelance rate.

If the user wants a spreadsheet (many founders do when money is involved), build
an editable .xlsx from `founder/plan.json` with live formulas and the inputs in
coloured cells, and check that its totals match `founder/money-plan.md`.

## Rules

- Every number in your note comes from the tool's output or an input you can name.
- VAT: prices and results are before VAT. VAT collected is not income; keep it
  apart and say when it is paid to the tax office (quarterly in the Netherlands).
- Revenue is before tax; say if the user's market adds sales tax on top.
- Not financial, tax or legal advice. Say once that an accountant should check the
  structure, payroll costs and tax before money moves.

## Output

Unit model: `founder/numbers.json`, `founder/cfo.md`, `founder/cfo-sources.md`.
Money plan: `founder/plan.json`, `founder/money-plan.md` (and the .xlsx if asked).
Next: `/founder-plan` uses these numbers for the verdict (the money plan's verdict
when `founder/plan.json` exists); `/founder-pricing` if the margin is thin.