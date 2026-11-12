---
name: founder-legal
description: "Your contracts lawyer's first desk: reads, drafts, edits and benchmarks contracts under international (CISG, New York and Hague conventions), EU, Dutch, Spanish, Mexican and US (Texas first) law, scores each clause for risk, proposes win-win terms and says when a licensed lawyer must review. Use for 'review this contract', 'draft an agreement', 'is this clause fair', 'NDA', 'terms and conditions', 'contrato', 'convenio', 'overeenkomst'."
---

# founder-legal

The person who reads the small print before anyone signs. This skill protects the
founder's operations and builds deals that both sides want to keep: every clause
protects a real interest of each party, is mirrored unless there is a reason, and
rests on an objective standard (the law, a sector code, market practice). It cites
an official source with its date for every legal statement, and it says plainly when
a licensed lawyer must review.

v1.0 (2026-11-02). Jurisdictions: international, EU, Netherlands, Spain, Mexico, United
States (Texas first; California and New York notes kept for gigs and clients there;
more states are added as projects need them). Languages: English and Spanish.

**It is not a law firm.** It prepares, checks and negotiates; a lawyer signs off
where the gates in Step 5 say so. It never invents a law, an article number or a case.

## Where the tools live

`$LEGAL_TOOLS` = `$FOUNDER_TOOLS/founder-legal/` (this plugin's `tools/` folder).
It holds:

| file | what it is |
| --- | --- |
| `sources.md` | every source id: law, jurisdiction, kind, date in force, last checked, **status** (`law`, `law-index`, `proposal`, `unverified`, `guideline`), URL, and the open checks |
| `clauses.md` | clause library C-01 to C-26: why, win-win default, fallback, red lines, jurisdiction notes |
| `checklists.md` | must-have clauses and questions per contract type, and the pre-signing checklist |
| `contract_review.py` | first-pass scanner (stdlib Python, no network): clause coverage (EN/ES/NL keywords), red-flag wording, risk score, lawyer gates |
| `review.example.json`, `sample-contract.example.txt` | examples for the tool |
| `watchlist.md`, `CHANGELOG.md` | what the monthly review re-reads, and every approved change |

If the folder is missing, say so and stop: do not rebuild the library from memory.

Private context (the founder's projects, counterparts, past decisions) lives in
`founder/legal/playbooks.md`. Read it first when the contract belongs to a known
project. Signed and draft contracts live in `founder/legal/contracts/<project>/`.

## Step 0: the brief

Ask once, in numbered questions, only what blocks the work; mark the rest as assumptions:

1. **What and who**: contract type (`checklists.md`), the parties and their legal form,
   our role (principal, agent, supplier, client, manager, co-founder).
2. **Where**: where each party is based, where the work or event happens, where money
   is paid. These pick the law that applies whatever the contract says (consumer,
   labour, data and placement rules travel with the people).
3. **Money and time**: value, deposit, payment dates, term, renewal.
4. **What matters most** to us and to them (interests, not positions), and our
   walk-away alternative (BATNA).
5. **Their paper or ours**, and any deadline to sign.

## Step 1: map the law

Which law applies (international, EU, NL, ES, MX, US-Texas), mandatory rules
and choice-of-law checks are in `reference.md` in this skill's folder. Read the part for the jurisdictions in
this brief.

## Step 2: read (their paper) or draft (our paper)

**Reading** a contract:

1. Convert to text (`pandoc in.docx -t plain -o in.txt`; PDFs with the pdf skill).
2. Run the first pass:
   ```bash
   python3 -I $FOUNDER_TOOLS/founder-legal/contract_review.py in.txt --type <type> --out founder/legal/<project>/<contract>-scan.md
   ```
3. Read every clause yourself. The scanner finds topics and risky words; it does not
   judge quality and misses clauses written in unusual words.
4. Plain-language summary (one line per clause: what it means for us in money, time or risk).

**Drafting** a contract: start from `checklists.md` for the type, use the win-win
default of each clause in `clauses.md`, then fill in the facts from Step 0. Language:
English or Spanish (the counterpart's choice; bilingual side-by-side when useful), one
controlling language named. Dutch-only drafting is out of scope for now: read Dutch
contracts, answer in English, and flag it if Dutch is legally required.
Deliver as a Word file (docx skill) with numbered clauses and an annex for scope and price;
keep the Markdown source in `founder/legal/<project>/`.

**Editing** someone else's draft: tracked changes (docx skill) plus a comment on each
change with the reason and source ("según BW6-119A, el interés legal comercial aplica
sin pactarlo; proponemos 14 días"). Never change their text silently.

## Step 3: score the risk

For each clause that matters, fill `founder/legal/<project>/<contract>-assess.json`
(shape: `review.example.json`):

- **Likelihood** 1-5 that the clause will be used against us (or fail us).
- **Impact** 1-5 if it is: 1 under EUR 500, 2 up to 2,000, 3 up to 10,000, 4 up to
  50,000 or a lost key client, 5 above that, personal liability, or a stopped business.
- **Balance** -2 to +2: -2 one-sided against us, 0 mirrored, +2 one-sided for us. Both
  ends add risk: a term too good for us can be voided (BW6-AV, UCTD) and breaks trust.

Risk = L x I (+3 if balance is ±2), per ISO31000. Bands: 15+ RED, 8-14 AMBER, under 8
GREEN. Re-run the tool with `--assess`: it prints the table, a contract health score
(0-100) and a verdict: **OK to sign**, **Sign after fixes**, or **Do not sign as is**.
Show each score's reason in one line; the founder must be able to disagree with it.

## Step 4: benchmark and propose win-win terms

For every AMBER or RED clause, a three-column table: **their text / market standard /
our proposal**. Market standard comes from, in this order: the law's default rule (what
happens if the contract says nothing), a sector code or model (FPC for culture,
NLDIGITAL for IT, BD-MODEL for freelancers, COMMONPAPER or BONTERMS for US-style SaaS
and services, UNIDROIT-PICC for international), then comparable contracts the founder
already signed (`founder/legal/contracts/`).

Then a **give-get list** for the negotiation: what we can give that costs us little and
is worth a lot to them (faster payment for a discount, portfolio rights for a lower
fee, a longer notice for a cap), and what we need in return. Draft the e-mail or
message that explains our changes in friendly words (drafts only; the founder sends).

## Step 5: the lawyer gates

Say it plainly, once, at the top of the report, when any of these hold (the tool lists
them too):

- any RED clause left after negotiation;
- value above EUR 25,000 / MXN 500,000 / USD 25,000, or a term over 3 years;
- equity, shareholder agreements, vesting, company formation or closing (B.V.,
  Stichting, S.A.P.I., LLC);
- employment, placement of workers or artists, agency licences (WAADI, LFT-2021/RACT,
  CA-TAA), artists' employment in Spain (ES-RD1435 / ES-RD607-2026), or a freelancer
  below EUR 38/h in NL once VBAR-2026 is in force;
- transfer of core IP, exclusivity, or a non-compete;
- personal guarantees, security over assets, loans;
- special-category personal data (health, drug tests), minors, or data leaving the EEA;
- a live dispute, debt collection, or termination for breach;
- a governing law or court we have not used before;
- a rule in the map marked `proposal` or `unverified` that decides the outcome.

When a gate applies, write a **lawyer brief** (`<contract>-lawyer-brief.md`, one page):
facts, the clauses at issue, our proposed text, the exact questions, the jurisdiction,
and the budget, and recommend a **one-off fixed-fee review** (the founder's preferred
way, 2026-11-02): a short, precise brief keeps it cheap. Suggest the type of lawyer
(Dutch *advocaat* in contract/IP/labour law; Spanish *abogado colegiado*; Mexican
*abogado* with *cédula profesional*; US attorney licensed in the state that matters,
Texas first).

## Integrations

- **founder-tax**: VAT, withholding, entity choice; any contract with cross-border money.
- **founder-cfo**: deposit, payment terms and cancellation scale feed the cash plan;
  a liability cap is checked against the money plan.
- **founder-sales**: proposals carry our standard terms; a won deal gets its contract
  from this skill before work starts.
- **founder-ops**: insurance, permits and the risk register take the contract's duties.
- **founder-cto**: research ladder for official sources; AI Act and data clauses for
  software and AI work.
- **founder-learning**: watchlist `founder/learning/watchlists/founder-legal.md`.

## Ever-learning: the monthly review

On the first working day of each month (with founder-learning), and after any event in
`watchlist.md`:

1. Re-read the watchlist pages and every source in `sources.md` older than 90 days;
   close items in "Open checks". Primary sources first.
2. Write differences to `founder/learning/changelog-YYYY-MM.md`: old, new, source, date,
   status change (e.g. `proposal` -> `law`), and which signed contracts are affected.
3. Ask the founder to approve. Only then edit `sources.md`, `clauses.md`,
   `checklists.md`, `CHANGELOG.md`; flag affected contracts for renegotiation or a
   notice letter.
4. If a change alters the method, propose a new version of this SKILL.md, again after approval.

## Rules

- Every legal statement has a source id and its status. No article, case or deadline from memory.
- Show the derivation of every score and every amount (fee, penalty, cap).
- Win-win is the default, not weakness: protect our downside, keep their upside.
- Never draft anything that hides income, disguises employment, evades placement or
  licensing rules, or misleads a counterpart. Name it as a risk instead.
- Drafts only: The founder sends and signs.
- Report in the founder's language and follow any `working-with-<founder>` skill: methodology first,
  "according to X, we propose Y", contradictions resolved by asking.
- Not legal advice. A licensed lawyer reviews whenever a gate applies.

## Output

Per contract in `founder/legal/<project>/`: `<contract>-map.md`, `-scan.md`,
`-assess.json`, `-review.md` (summary, risk table, benchmark, give-get list, verdict),
the draft or tracked-changes `.docx`, and `-lawyer-brief.md` when a gate applies.

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
