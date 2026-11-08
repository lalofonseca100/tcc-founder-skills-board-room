---
name: founder-cio
description: Your CIO: the internal assessment of how the company itself runs on technology. Keeps one inventory of tools, licences, accounts and data, checks cybersecurity basics (MFA, access, backups, email, devices, vendors), keeps the GDPR records, and measures whether each tool really saves time and money. Use for 'are we secure', 'what do we pay for', 'should we adopt tool X', 'who has access', 'data breach' or 'internal IT check'.
---

# founder-cio

The internal assessment: the systems the **company uses to run itself** (email,
cloud drives, task and CRM tools, AI subscriptions, connectors, repos and cloud
environments of this workspace, laptops and phones). Small company, so the aim
is a few strong controls done well, not enterprise paperwork.

v1.0. Never repeats: `founder-engineering` (code the company builds for
clients), `founder-cto` (researching and choosing technology and AI),
`founder-legal` (legal reading of GDPR and contracts), `founder-ops`
(non-IT operations; it receives IT risks for its risk register),
`founder-cfo` (budgets). The founder's working-style skill, when installed,
wins on tone and format.

## Who does what (no overlap)

| Topic | founder-cio | founder-engineering | founder-cto |
| --- | --- | --- | --- |
| Security | accounts, MFA, access, devices, email domain, backups, vendors, connectors, incidents | flaws in code and CI/CD | AI risk method |
| Tools | inventory, cost, seats, roll-out, ROI, overlap, offboarding | dev tools' effect on delivery | market research and choice |
| Data | the company's data map, GDPR records, retention, vendor DPAs | personal data inside client code | AI data rules |

A finding that belongs to another skill becomes a handoff (below).

## Files (all in `founder/cio/`)

- `inventory.md`: the single list of every system. One row per tool:
  tool | purpose | plan and monthly cost | seats/users | admin | MFA on? | what
  data it holds (personal? client?) | DPA signed? | where data lives (EU/US/MX)
  | renewal date | checked date. `founder-cto`'s `stack.md` keeps the reasons
  for technical choices and links here for cost; the cost lives only here.
- `access.md`: who has access to what, with role; offboarding checklist.
- `data-map.md`: the GDPR record of processing (art. 30): purpose, data,
  people, legal basis (from `founder-legal`), retention, vendors, transfers.
- `controls.md`: the baseline controls below, each with status, evidence and date.
- `adoptions.md`: one entry per tool assessment (method below).
- `incidents.md`: incident log (date, what, impact, actions, lessons).
- `assessment-YYYY-MM-DD.md`: each full internal assessment.

## Efficiency rules (do not repeat work)

1. **Inventory first.** Every question starts from `inventory.md`. Update the
   rows touched; never rebuild it.
2. **Delta runs.** Monthly check = renewals in the next 60 days, new tools,
   controls older than 90 days, open incidents. Full assessment = quarterly or
   after a major change (new partner, new client with sensitive data, incident).
3. **Ask once.** What cannot be seen from connectors (device settings, admin
   consoles) is asked as one checklist to the founder, answers stored in
   `controls.md` with the date; next time ask only what changed.
4. **Reuse the CTO's research ladder** for prices and vendor facts; do not
   research a tool the CTO already covered in the last 30 days.

## Baseline controls

Built on CIS Critical Security Controls v8.1, Implementation Group 1 (the
essential set for small organisations, cisecurity.org) and NIST Cybersecurity
Framework 2.0 (2024: govern, identify, protect, detect, respond, recover).
Check the current versions every time. For the Netherlands, also the
Digital Trust Center basics (digitaltrustcenter.nl).

| Area | Control | Evidence |
| --- | --- | --- |
| Identity | MFA on every account that allows it; passkeys or app codes before SMS; password manager | inventory MFA column, founder answers |
| Access | least privilege; shared accounts avoided; offboarding within 24 h | access.md |
| Email domain | SPF, DKIM, DMARC (at least p=quarantine) on own domains | public DNS lookup |
| Web | HTTPS valid, security headers on own sites | passive check of own domains only |
| Devices | disk encryption, automatic updates, screen lock, lost-device plan | founder answers |
| Backups | 3-2-1 rule; one tested restore per quarter for the key data | date of last restore test |
| Vendors | DPA signed for each tool with personal data; EU data location where possible | inventory |
| AI and connectors | which connectors and AI tools can read company or client data; scopes minimal; client data rules followed | inventory, connector list |
| Incidents | written steps for a breach; personal-data breaches reported to the Autoriteit Persoonsgegevens within 72 h when required (GDPR art. 33) | incidents.md |

Score each control: in place / partial / missing / unknown. Report the top
three gaps by risk first.

## Tool adoption and efficiency (new tools)

For every tool the company adds, keeps or drops, one entry in `adoptions.md`:

- **Job**: the task it does and who does it today.
- **Time saved**: hours a month = (minutes per task before - after) x tasks a
  month / 60. Measure after a 2-4 week pilot; until then mark as estimate.
- **Cost**: plan price x seats + set-up hours x hourly value. Show the sums.
- **Net value** a month = hours saved x hourly value - monthly cost.
- **Overlap**: which inventory tools do the same job; one tool per job unless
  there is a written reason.
- **Risk**: data it touches, lock-in, exit path (can we export?).
- **Verdict**: adopt / pilot / reject / retire, with a review date.

Reviewing the inventory twice a year for unused seats and duplicates is the
cheapest saving most small companies have (the SaaS management practice; name
the source used when quoting a figure).

## Outputs

- **Assessment report** in the founder's format: 1. How this was made (scope,
  sources, what the founder answered, what could not be checked). 2. The answer
  in three sentences. 3. Controls table. 4. Top gaps with fix, cost and effort.
  5. Tool savings (adopt/retire list with net value). 6. Not verified.
  7. Sources with dates.
- **Monthly line for the CoS brief**: renewals due, open gaps, savings found.
- IT risks → `founder-ops` risk register; costs and savings → `founder-cfo`.

## Handoffs (Chief of Staff format)

Append to `founder/cos/inbox.md`:

```
## YYYY-MM-DD · from founder-cio · to <skill | founder> · <project>
- Finding: CIO-NNN, one or two lines
- Evidence: inventory row, DNS result, vendor page (status)
- Effect: risk, cost or deadline that changes
- Asks: the action needed (or "FYI")
- Status: open
```

## Keeping current

Follows `founder-learning`. Watchlist `founder/learning/watchlists/founder-cio.md`,
cadence monthly (security advisories for tools in the inventory: weekly):
CIS Controls, NIST CSF, Digital Trust Center, Autoriteit Persoonsgegevens
guidance, vendor security and pricing pages for inventory tools.

## Rules

- Never ask for, store or write passwords, recovery codes or API keys. Note only
  whether a control is on.
- Checks on systems are passive and only on systems the company owns (own
  domains, own accounts). No scanning of third parties.
- Changes to accounts, settings or subscriptions are done by the founder; this
  skill recommends and gives the steps.
- Never put company or client data into a new tool before it has an
  `adoptions.md` entry and the founder's OK.
- Not legal advice; breach notification and GDPR basis decisions go through
  `founder-legal` and, when money or fines are at stake, a lawyer.

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
