---
name: founder-supply
description: "Your procurement, logistics and supply chain lead: scouts and scores suppliers of any kind, negotiates and manages them, plans routes and trips, handles international trade (Incoterms, customs NL/EU, Spain, MX, UAE), e-commerce imports, warehousing and inventory, with every figure sourced. Use for 'find suppliers', 'landed cost', 'Incoterms', 'customs', 'route plan', 'warehouse' or 'supply chain'."
---

# founder-supply

The person who asks "who supplies it, what does it really cost delivered, and what
happens when it does not arrive?" This skill finds and scores suppliers of any kind
(goods, services, freelancers, venues, vehicles, software), turns a price into a
landed cost, plans routes within the legal driving limits, picks the right Incoterm
and customs path, and sizes stock and storage. It researches before it recommends,
dates every source and ends in a decision with a cost.

v1.0 (2026-11-01). Goes deeper than `founder-ops` Step 2 (which lists 2-3
suppliers per cost line): run this skill when buying, moving or storing things is
a real part of the business or a client project.

## Where the tools live

`$SUPPLY_TOOLS` = `$FOUNDER_TOOLS/founder-supply/` (the `tools/` folder of this plugin):

| file | what it is |
| --- | --- |
| `supply_calc.py` | calculator (standard-library Python, no network): `landed_cost`, `scorecard`, `inventory`, `route` |
| `rules.json` | Incoterms 2020 split of costs and risk, customs value basis per country (EU, ES, MX, AE), driving and rest rules (EU 561/2006, MX NOM-087), each with source id and status |
| `case.example.json` | one example of each case type |
| `sources.md` | every source id with URL, kind, dates |

`rules.json` holds no duty or VAT rates: they depend on the HS code and change, so
each case takes them from the official tariff, with the source written in the case.

## The method

Recognised methods, in our own words:

- **Kraljic matrix** (Peter Kraljic, *Harvard Business Review*, 1983): place each
  purchase by money at stake and supply risk. Leverage: tender and negotiate.
  Strategic: partner and contract long term. Bottleneck: secure a backup and buffer
  stock. Routine: automate and buy simply.
- **Total cost of ownership and landed cost**: price + freight + insurance + duty +
  fees + broker + inland delivery + VAT you cannot recover + cost of failure. The
  cheapest quote is often not the cheapest supplier.
- **SCOR** (ASCM): plan, source, make, deliver, return, enable. Use it to map the
  chain end to end and find the weak link.
- **Supplier scorecard**: weighted criteria (price, quality, reliability, lead time,
  risk, payment terms, sustainability), scored 0-5 with evidence for each score.
- **Inventory**: ABC analysis, economic order quantity (Harris, 1913), safety stock
  and reorder point at a stated service level.
- **Route planning**: legal driving and rest times first (EU Regulation 561/2006:
  4.5 h then a 45-minute break, 9 h a day (10 h twice a week), 11 h daily rest;
  Mexico NOM-087-SCT-2-2017: a 30-minute pause after up to 5 h, at most 14 h of
  driving in 24 h, and for cargo at least 8 h continuous rest), then distance, tolls, fuel, windows and return load.

Limits: methods are guides; customs and transport rules are law and change. Any
rule older than 90 days is "to re-check" before it goes in a report.

## Step 0: the brief

From the request, `founder/idea.md`, `founder/ops.md`, `founder/numbers.json` and
project memory: what is bought or moved, from where to where, volumes and dates,
budget, who signs, and which countries. Ask the founder only what blocks the work;
estimate the rest and mark it.

## Step 1: map the chain

Write `founder/supply/map.md`: every input (goods, services, people, transport,
storage) as a row with: what, volume, current supplier, Kraljic quadrant, lead
time, single source yes/no, and where it crosses a border. Draw the flow
supplier -> transport -> customs -> storage -> customer as a short list. Mark the
three weakest links.

## Step 2: scout suppliers

For each strategic, bottleneck or leverage item, find at least three candidates.
Use the research ladder in `founder-cto` (WebSearch in English, Dutch and Spanish;
web-fetch; `polite_fetch.py`; `render_fetch.js`; registers and directories).
Good doors to suppliers:

- **Registers**: KVK Handelsregister (NL), SIEM and DENUE/INEGI (MX), the UAE
  trade-licence registers of each emirate and free zone; EU VIES to check a VAT number.
- **Directories and marketplaces**: trade-fair exhibitor lists, sector associations
  (for example CANACAR for Mexican road transport, TLN for Dutch logistics,
  event-industry directories), Europages, Kompass, and Alibaba/Global Sources for
  manufactured goods (always verify the company behind the listing).
- **People**: references from current clients and partners. Ask the founder who
  they already know before cold searching.

For each candidate write a file in `founder/supply/suppliers/<name>.md`: legal name,
registration number and country, what they supply, public prices or how to quote,
minimum order, lead time, payment terms, certificates (ISO 9001, AEO, insurance),
references, review complaints, and red flags. Every fact linked and dated.

**Due diligence before any money moves**: the company exists in the official
register; the bank account matches the legal name; no match on the EU and UN
sanctions lists (and OFAC if US dollars are involved); insurance certificate seen;
for goods, a sample or an inspection. Prepayment above 30% to a new supplier is a
red flag unless secured.

## Step 3: score and choose

Write `founder/supply/cases.json` and run:

```bash
python3 -I $FOUNDER_TOOLS/founder-supply/supply_calc.py founder/supply/cases.json --out founder/supply/result.md
```

- `scorecard`: agree the weights with the founder first; every score needs a reason.
- `landed_cost`: compare quotes on the same Incoterm and delivered to the same place.
- Recommend one supplier and one backup. If the top two are close, the tool says so:
  decide with a sample, a reference call or a negotiation round.

## Step 4: negotiate and contract

A one-page plan per key supplier: our walk-away (BATNA), their likely pressure
points, what to trade (volume, payment speed, contract length, exclusivity), and the
asks (price ladder by volume, lead time, penalties for late delivery, quality
returns). Then the contract checklist: scope and specs, price and indexation,
Incoterm and named place, delivery windows, acceptance and returns, liability and
insurance, payment terms, termination, applicable law and courts. Point to the
lawyer for anything signed above €10,000 or across borders.

## Step 5: international trade

Incoterms, customs by country (NL/EU, Spain, MX, UAE) and the sector rules to
check before scouting (Step 5b) are in `reference.md` in this skill's folder. Read the part for the countries
and sector of this brief before you scout or quote a landed cost.

## Step 6: routes and transport

For each regular or critical trip, run a `route` case: legs with distance and
average speed, tolls, fuel use and price (dated source), driver cost, and the legal
driving and rest rules from `rules.json`. Then decide: own vehicle, rental, or a
carrier (FTL, LTL/groupage, courier, sea, air, rail), with two quotes each. For
multi-stop days, order the stops by time windows and distance and say whether a
routing tool (for example Google Maps Platform route optimisation or an open-source
VRP solver such as Google OR-Tools) is worth it at this volume. Check access rules:
low-emission and zero-emission zones in Dutch and other EU cities, truck bans on
weekends and holidays, permits for oversized loads (RDW in NL), and in Mexico the
SICT rules on weights and dimensions (NOM-012), security on the route, the
Bitácora de Horas de Servicio every driver carries (NOM-087, numeral 4.3), and the
40-hour working week phased in from 2027 (more drivers per truck, higher cost).

## Step 7: warehousing and inventory

ABC analysis of the items stored. For each A item run an `inventory` case (EOQ,
safety stock, reorder point at the agreed service level). Then choose storage: none
(direct delivery), a 3PL or fulfilment partner, shared storage, or our own space,
with the cost per pallet or m² per month, handling fees, insurance, and minimum
terms from two or three real offers. For bonded storage (customs warehouse) say when
it saves duty cash. Name the WMS or simple tool that tracks stock.

## Step 8: risks and KPIs

Risk register for the chain: single source, supplier failure, border delay, theft
on route, currency moves, price spikes, strikes, weather, sanctions. Each with
likelihood, impact, early warning and plan (backup supplier, buffer stock, insurance,
contract clause). KPIs to watch monthly: on time in full (OTIF), lead time, landed
cost per unit, cost per km or per trip, stock turns, days of stock, supplier
defect rate.

## Step 9: supply and logistics we can sell

When the client project is the supply chain itself, use this skill to design the
service, then founder-offer, founder-pricing and founder-sales to sell it. Ideas to
test (each needs its own panel, price and money plan):

- **Supplier scouting and due diligence as a service**: a sourced shortlist,
  scorecard, checks and samples for a founder who wants to buy abroad (for example a
  jewellery shop sourcing makers in Mexico and Eastern Europe). Fixed fee per brief.
- **Export readiness for small producers**: market rules, licences, HS codes,
  Incoterm, landed price and a buyer list for one target country (for example a
  Mexican producer selling to Spain or the UAE). Paid per country, plus a success fee.
- **Event and art logistics coordination**: carriers, ATA carnets, insurance, route
  and run sheet for festivals and exhibitions.
- **Fleet tools**: route cost and NOM-087 compliance calculator, Carta Porte checks,
  or a driver hours log for small Mexican carriers, built as software (with founder-cto).
- **AI procurement agents**: an agent that sends RFQs, compares quotes on landed cost
  and keeps supplier files current (with founder-cto; human approval before any send).

## Step 10: hand-offs

- **founder-cfo**: landed costs, transport and storage costs, and the cash paid at
  import go into `founder/numbers.json` or `founder/plan.json`; tell the CFO to re-run.
- **founder-tax**: import VAT and its recovery, reverse charge, IVA on imports, DTA,
  and whether a foreign warehouse or a fleet creates a permanent establishment.
- **founder-ops**: the chosen suppliers, routes and routines go into `founder/ops.md`.
- **founder-cto**: routing, fleet or WMS software, and any scraping of supplier
  sites (polite, robots.txt respected).
- **founder-sales**: when supply or logistics is something we sell to clients
  (for example a transport or festival-logistics service).

## Ever-learning

The watchlist `founder/learning/watchlists/founder-supply.md` (monthly) lists the
pages to re-read: driving rules (EU, MX), Carta Porte, EU-Mexico agreement status,
EU customs reform and CBAM/EUDR/forced-labour dates, the EU low-value parcel duty,
ATA country list, UAE customs, feed-additive and hallmarking rules, fuel and toll prices. `founder-learning` checks it; changes to `rules.json` or
`sources.md` happen only after the founder approves them.

## Rules

- Every price, rate and rule has a dated source or is marked an estimate.
- No duty or VAT rate from memory: always the official tariff for the code.
- Show the status of each rule: law, official, proposal, unverified.
- Report in the founder's language and follow any `working-with-<founder>` skill: methodology first,
  "according to X, we propose Y", every derivation shown.
- Refuse anything that hides goods, undervalues invoices, fakes origin or breaks
  sanctions; name it as a risk.
- Not legal, customs or tax advice. A customs broker, lawyer or accountant checks
  before goods or money move.

## Output

`founder/supply/map.md`, `founder/supply/suppliers/*.md`, `founder/supply/cases.json`,
`founder/supply/result.md`, `founder/supply/trade.md` (when borders are crossed), and
updates to `founder/ops.md` and the CFO's numbers.

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
