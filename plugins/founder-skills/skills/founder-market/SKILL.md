---
name: founder-market
description: Your market analyst: sizes the market bottom-up and top-down from public sources (total, reachable, winnable in 3 years), with trends, ups and downs, and which country or segment to start in. Use for 'how big is the market' or 'market research'.
---

# founder-market

A business can only sell into the market that exists. This skill counts it: how
many buyers there really are, what they spend a year, how much of that this
business can reach and win, and which way the market is moving. Every number is
shown as a sum anyone can redo.

## The method

Market sizing in three layers, built from the bottom up first, as taught in Bill
Aulet's *Disciplined Entrepreneurship* (2013, step 4: the beachhead market's total
addressable market) and in Steve Blank and Bob Dorf's *The Startup Owner's Manual*
(2012: total, served and target market). Summaries in our own words:

- **Total market (TAM)**: every buyer who has this need, times what each spends on
  it a year.
- **Reachable market (SAM)**: the part this business can serve with its offer,
  place, language and channels today.
- **Winnable in 3 years (SOM)**: the share it can realistically win, limited by
  capacity, sales cycle and competitors.

**Bottom-up is the main number**: count the buyers (from registers, member lists,
event calendars, company databases) and multiply by a spend per buyer you can
source. **Top-down is the check**: an industry report's total, cut down to the
segment. If the two differ by more than about 3 times, say so and explain which
one you trust and why.

## Step 1: define the buyer and the job

From `founder/idea.md` (write it first if missing; see `/founder-board` step 0),
`founder/competitors.md` and `founder/customer.json` if they exist: who pays, for
what job, in which countries. Split into 2 to 5 segments that buy differently
(for an art agency: festivals, municipalities, brand agencies, venues). Ask the
user which countries are in scope if it is not clear.

## Step 2: count the buyers (bottom-up)

Per segment and country, the number of buyers, each with a link: official
statistics (CBS and Eurostat for the Netherlands and the EU, national statistics
offices elsewhere), business registers (KvK), industry associations and their
member lists, event databases, public tenders (TenderNed, TED), annual reports.
Then the share that buys this kind of thing at all, and how often a year.

## Step 3: spend per buyer

What a buyer spends a year on this job, from: the business's own quotes and
prices (`founder/pricing.md`, `founder/plan.json`), competitors' public prices
(`founder/competitors.md`), published budgets (municipal budgets, festival annual
reports, subsidy awards), and industry reports. Give a low and a high figure, never
one number.

## Step 4: the three layers and the check

```
TAM = buyers x share that buys x purchases a year x spend per purchase
SAM = TAM x share this business can serve (offer, place, language, channels)
SOM = the lower of: SAM x a realistic 3-year share, and what capacity allows
```

Show each multiplication with its inputs and sources, low and high. Write the
reasoning for every share; a share without a reason is a guess, and must be marked
as one. Then the top-down check from a sourced industry figure.

Compare the SOM with the units the CFO planned (`founder/plan.json` or
`founder/numbers.json`): if the plan needs more than about a third of the SOM in
any year, flag it as optimistic.

## Step 5: trends, ups and downs

For each segment, the three to five forces that move it, each with a source and a
direction (up, down, uncertain): demand (attendance, budgets, subsidies), money
(public budget cuts, corporate marketing spend, interest rates), rules (permits,
sustainability reporting, safety), climate and season (heat cancellations, wet
summers), technology, and new competitors. Be critical: give the downside as much
space as the upside, with the worst recent year as an example.

## Step 6: where to start

A table of the segments (and countries, if more than one) scored on size (SOM),
growth, ease of reaching the buyer, sales cycle length and fit with the founders'
network. Recommend one beachhead: the smallest segment the business can win first
and use as proof for the next one. Say what would make you change the pick.

## Rules

- Every number has a link or is marked as an estimate with its reasoning. Never
  invent a market size, a growth rate or a report.
- Quote a paid report only from its public summary, and say so.
- Ranges, not points. Round to two significant figures; false precision hides
  guesses.
- Market size is not demand: a big market says nothing about whether buyers will
  pick this business. Say this once.
- Not investment advice.

## Output

`founder/market.md` (method, segments, the three layers with sums, the check,
trends, where to start, the source list) and `founder/market.csv`
(`segment,country,buyers,share_buying,purchases_per_year,spend_low,spend_high,tam_low,tam_high,sam_low,sam_high,som_low,som_high,sources`).
It answers the board's open question on market size and caps the CFO's units.
Next: `/founder-consumer` for the buyers in the chosen segment, `/founder-cfo` to
check the plan against the SOM, `/founder-marketing` for the beachhead.

## Where it sits in the pack

```
board -> market -> competitors -> consumer -> pricing -> offer -> cfo -> marketing -> brand -> ops -> launch -> plan
```
