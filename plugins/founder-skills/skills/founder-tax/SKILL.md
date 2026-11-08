---
name: "founder-tax"
description: "Tax advisor for the Netherlands, Mexico, Spain and the UAE: real tax per regime, VAT, treaties and legal benefits, every figure sourced and dated. Use for 'how much tax', 'BV or eenmanszaak', 'RESICO', 'autónomo', 'UAE company'."
---

# founder-tax

The person who asks "and what is left after tax?" This skill turns a profit or
income into the tax actually paid in the Netherlands (NL), Mexico (MX), Spain
(ES, Illes Balears scale by default) or the United Arab Emirates (AE), shows
every step with its source, compares structures, and lists the legal benefits
the founder is missing. It never invents a rate: every number comes from
`rules.json`, which carries a source and a date.

## Where the tools live

`$TAX_TOOLS` = `$FOUNDER_TOOLS/founder-tax/` (the `tools/` folder of this plugin). It holds:

| file | what it is |
| --- | --- |
| `rules.json` | every rate, bracket and limit per country and year, with source id and status (`law`, `proposal`, `approved_lower`, `unverified`) |
| `tax_calc.py` | the calculator (standard-library Python, no network) |
| `case.example.json`, `case.example2.json` | example cases (NL, MX; ES, AE) |
| `sources.md` | every source id with URL, kind (primary/secondary), publish date and last check |
| `watchlist.md` | official pages and the yearly calendar the review re-reads |
| `CHANGELOG.md` | every change to `rules.json`, approved by the founder |

If the folder is missing, say so and stop: do not rebuild rates from memory.

## Step 0: the facts only the founder knows

Read `founder/tax/profile.md` first. Ask only what is missing, once, in numbered
questions, and record the answers there:

1. **Tax residence** of each founder: country, days per year in each, where the
   permanent home and family are. Dual residence decides everything else.
2. **Legal form** in each country: eenmanszaak / BV / Stichting (NL); RFC and
   régimen: RESICO, actividad empresarial, sueldos, persona moral (MX);
   autónomo / SL and comunidad autónoma (ES); mainland or free zone (AE).
3. **Who pays whom**: clients' countries, whether clients are companies or
   people, currency, and where the work is physically done.
4. **Hours** per founder per year (NL urencriterium: 1,225) and whether they are
   starters (first 5 years).
5. **Advisors**: The founder's accountant in each country.

Until answered, run with clearly marked assumptions.

## Step 1: map the rules that apply

Write `founder/tax/map.md`: one table per country listing each tax that applies
(income tax, social/health contribution, BTW/IVA, corporate tax, dividend tax,
withholdings), the regime, the rate from `rules.json`, its source id and its
status. Then the **connections** between countries:

- **Who taxes first (NL-MX treaty 1993, art. 4)**: permanent home, then centre of
  vital interests, habitual abode, nationality, mutual agreement.
- **Work done in the other country**: independent services are taxed there only
  with a fixed base or 183+ days in 12 months (art. 14). Construction or
  installation creates a PE after 6 months (art. 5); the treaty has no service PE.
- **Artists and performers (art. 17)**: taxable where they perform, also when the
  fee is paid to an agency. Matters for artists touring between NL
  and MX. Check NL's artiestenregeling for treaty residents before assuming a
  withholding.
- **Relief**: NL exempts (with progression) or credits; MX credits up to the
  Mexican tax. Dividends from a company: 5% (company holding 10%+) or 15%.
- **VAT across borders**: B2B services to an EU business are usually reverse
  charge; services exported from MX can be 0% IVA when they meet the export rules.
  Confirm per case.
- **Spain**: residence after 183 days or centre of economic interests; IRPF
  has a state and a regional half (Baleares by default). Non-resident artists
  performing in Spain face IRNR withholding (check the rate and treaty).
- **UAE**: no personal income tax, corporate tax 0%/9%, Small Business Relief
  up to AED 3M revenue. For a founder resident elsewhere (for example NL), the UAE
  result is only half the picture: NL taxes worldwide income, and a UAE company
  run from NL can be Dutch tax resident. Always run the home-country case too.

Open items in `sources.md` (for example treaty interest and royalty rates) are
stated as open in every report that depends on them.

## Step 2: run the numbers

Write `founder/tax/cases.json` (shape: `$TAX_TOOLS/case.example.json`):

| regime | fields |
| --- | --- |
| NL `eenmanszaak` | `profit`, `turnover`, `urencriterium`, `starter` |
| NL `bv` | `profit` (before DGA salary), `dga_salary` (default gebruikelijk loon), `distribute` |
| MX `resico_pf` | `income` (collected, before IVA), `costs` (paid, not deductible) |
| MX `pf_empresarial` | `income`, `deductions` (with CFDI) |
| MX `pm` | `profit` (resultado fiscal), `distribute` |
| ES `autonomo` | `income`, `expenses`, `new_autonomo` (tarifa plana €80/month) |
| ES `sl` | `profit`, `new_company` (15%), `distribute` |
| AE `business` | `revenue`, `profit`, `elect_sbr`, `free_zone_qualifying` |

```bash
python3 -I $FOUNDER_TOOLS/founder-tax/tax_calc.py founder/tax/cases.json --out founder/tax/result.md
```

Each case prints a table: step, amount, rule, source id, plus warnings for any
value that is a proposal, unverified, or copied from the previous year. Put
those warnings in the report; never drop them.

Always run **at least two cases** to compare: this year vs next year (when a
reform is announced), or eenmanszaak vs BV, or RESICO vs actividad empresarial,
or the same income in two countries.

## Step 3: legal benefits checklist

For each item: does it apply, the money it changes (run the case with and
without it), the condition, and the source. Only legal, documented options.

NL: urencriterium (zelfstandigenaftrek, startersaftrek: 2026 is the last useful
year, it falls to €10 in 2027 under the proposal), MKB-winstvrijstelling, KOR
under €20,000 turnover, KIA on investments, WBSO and innovatiebox for software
R&D, BV once profit is high enough to beat the extra costs, 30% ruling for hires
from abroad (27% from 2027).
MX: RESICO vs actividad empresarial (RESICO wins when real costs are low; it
loses when costs are high, since costs are not deductible; RESICO likely needs
Mexican residence), the optional 7% IVA in RESICO from 2027 (only if approved
and only if IVA on costs is small), deducciones personales (cap 5 UMA or 15% of
income), PPR/retirement deductions, the border region incentive (8% IVA) if the
business qualifies, and the 2027 regularisation programme for old debts.
ES: tarifa plana (€80/month first 12 months), 5% gastos de difícil
justificación (cap €2,000), IS 15% for new companies and startups (Ley 28/2022),
micro-company IS scale, Beckham regime for people moving to Spain.
AE: Small Business Relief (check it still applies after 2026), Qualifying Free
Zone 0% on qualifying income, no tax on personal income; only real if the
substance and residence are really in the UAE.

Anything that relies on hiding income, fake invoices, sham residence or
artificial structures is refused and named as a risk, not a benefit.

## Step 4: hand-off to the CFO

- From `founder/money-plan.md` (founder-cfo): take each year's result per founder
  (eenmanszaak, autónomo) or per company (BV, SL, persona moral, UAE company) as
  `profit`, run the cases, and add a line "after tax" per year to the CFO note.
- Use the VAT rate from `rules.json` for `vat_rate` in `founder/plan.json`.
- In MXN plans, set aside ISR monthly (RESICO: rate × collections) and IVA monthly.

## Step 5: when to call the advisor

Say it plainly, once, at the top of the report, when any of these hold:
dual residence or moving country; any UAE structure for a non-UAE resident;
setting up or closing a BV, SL, Stichting or persona moral; invoicing across
borders; first employee or payroll; any treaty claim; amounts over €50,000
profit or MXN 1,000,000 income; any value in the calculation marked
`unverified` or `proposal` that changes the decision.

## Ever-learning: the monthly review

Run on the first working day of each month (a routine can trigger it), and
always after the calendar dates in `watchlist.md` (Prinsjesdag, Paquete
Económico, DOF, Eerste Kamer, Anexo 8, UMA, Spanish Presupuestos and BOE,
UAE FTA decisions):

1. Re-read every page in `watchlist.md` and every source in `sources.md` older
   than 90 days. Primary sources first.
2. Write the differences to `founder/learning/changelog-YYYY-MM.md`
   (the shared changelog of all founder skills): old value, new value, source,
   date, status change (for example `proposal` → `law`).
3. Ask the founder to approve the list. Only then update `rules.json`, `sources.md`
   (last checked date) and `CHANGELOG.md`, and re-run the cases of active projects.
4. If a rule change alters the skill's method (not just a number), propose a new
   version of this SKILL.md, again after the founder approves.

## Rules

- Every number comes from `rules.json` or the founder's input. No rate from memory.
- Show the status of each figure: law, proposal, approved by one chamber, unverified.
- Report in the founder's language and follow any `working-with-<founder>` skill: methodology first,
  "according to X, we propose Y", every derivation shown.
- Results are before personal situations the tool does not model (partner,
  children, mortgage, box 3 assets, PTU, Spanish family minimums, payroll). Say
  what was left out.
- Not tax advice. An accountant checks before money moves.

## Output

`founder/tax/profile.md`, `founder/tax/map.md`, `founder/tax/cases.json`,
`founder/tax/result.md` (with the CFO hand-off), and the changelog entry when a
review runs.

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
