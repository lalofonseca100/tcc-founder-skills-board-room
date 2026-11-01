---
name: "founder-sales"
description: "Your B2B sales lead: ideal client and buying signals, a sourced target list, account files, one outreach draft per role, discovery calls, proposals, and a pipeline kept in the company's own CRM with evidence. Use for 'find clients', 'outreach', 'follow up', 'update the CRM' or 'pipeline review'."
---

# founder-sales

B2B clients rarely buy from an ad. They buy after a well-timed message, a good
call and a clear proposal. This skill runs that loop for every project of the
company (agency services, software and media work). It keeps
every lead in one place, and it never sends anything without the founder's OK.

The account file, the role-based email and the evidence rules for stages are
adapted from `hiveflowai/claude-para-revenue` (MIT licence, Jonathan Olvera,
2026). Discovery questions follow Rob Fitzpatrick's *The Mom Test* (2013):
ask about the past and real behaviour, not opinions about the future.

## The CRM

The pipeline lives in a CRM Artifact with a shared database (its URL is kept in
`founder/sales/crm.md`; if there is none, offer to build one). Collection `deals`,
one document per account or deal:

`name, project, contact, role, reach, owner, value_low, value_high (euros, excl.
VAT, revenue to that project), expected, fit (0-100), source, stage, next_step,
next_date (YYYY-MM-DD), updated, notes [{date, text}]`

Stages: `lead`, `researched`, `contacted`, `meeting`, `proposal`, `won`, `lost`,
`partner`.

Read and write it with the `ArtifactData` tool (`list` or `query` on `deals`;
`set` or `update` pinned with `if_version` from your last read; `batch` for more
than two). Always search for the account before you create one: never make a
duplicate. Never delete a deal or a note. The founders also edit it on the page.

Connectors: Gmail (**drafts only**), Google Calendar, Google Drive. If one is not
connected, say which and carry on without it.

## Step 1: the ideal client and the signals

Per project, write `founder/sales/icp-<project>.md` from `founder/idea.md`,
`founder/market.md` (the beachhead), `founder/pricing.md` and `founder/plan.json`:

- **Who buys**: type of organisation, size, country, and the role that signs
  and the role that has the problem.
- **Not for us**: who we do not sell to, and why.
- **Buying signals**, strongest first, each with points. Fit = base + signals,
  maximum 100; **below 40, do not contact yet**. Examples for an art agency: a
  festival announces its next edition or theme (+25); a public tender or a
  municipal budget for public art or placemaking (+25); a new head of programme
  or production in the last 90 days (+20); the festival used large-scale art
  before (+15); a sustainability or reuse goal in their report (+10). For
  software and media work: a job ad for the role our work replaces (+25); a new
  product or site launch (+20); a funding round or grant award (+15).
- **Base fit**: size in range (30), sector where we already have a client (20),
  country we serve (10).

Ask the founder to correct the profile before you build the list.

## Step 2: the target list

Find 20 to 50 accounts from public sources, each with a link: festival and event
calendars, TenderNed and TED (public tenders), municipal sites, KvK, industry
associations, event agencies' client pages, LinkedIn company pages (read only).
Add each one to the CRM as `lead` with its `source`. Do not buy contact data.

## Step 3: the account file

For each account worth contacting, write `founder/sales/accounts/<slug>.md` in
two minutes' reading:

```markdown
# <Account> · fit <0-100>
**What they do:** who they sell to, what, size. (source)
**Why now:** the buying signal. (source) Or: "no signal found".
**Who decides:** <role> · **Who has the problem:** <role>
**How to start:** the angle of the first message, tied to the signal.
**Sources:** 1. ... 2. ...
```

Names of people only if a public source shows them, with the source. Never invent
a figure, a client or a name: write "no data". Then set the deal to `researched`
with the fit score.

## Step 4: one draft per person

For each contact, one message about **their** problem, by role (for example:
the festival director wants a programme that sells tickets; the production
manager wants nothing that fails a safety check; the municipal officer wants a
project that passes council and the budget). Rules:

- At most 90 words. Subject at most 6 words, no capitals or emoji.
- Open with the signal ("I saw that ..."), not with us. One idea of value, with a
  number only if it is real and checkable. Close with an easy question, not "can
  we book 30 minutes?".
- The tone of a colleague who did their homework. English unless the account
  works in Dutch or Spanish.
- **Mark `REVIEW` and stop** if a draft mentions a price, a discount, a client by
  name, or a promised result; say why.
- Save as Gmail drafts (or in `founder/sales/drafts.md`). **Never send.** The
  founder sends. When they confirm it went out, move the deal to `contacted`.
- Before any bulk outreach, remind the founder once: in the Netherlands, cold
  email to a company address needs an opt-out line, and sole traders and
  private people need consent first; check with ACM and Autoriteit
  Persoonsgegevens guidance. Not legal advice.

## Step 5: the discovery call

Before a meeting, write `founder/sales/calls/<slug>-<date>.md`: the account file,
three things to learn, and the questions:

- "Tell me about the last time you programmed art / commissioned this kind of
  work. What happened? What went wrong?"
- "Who else was involved in that decision? How was it paid for?"
- "What did it cost, and where did the budget come from?"
- "What would have to be true for you to do this again next season?"
- Avoid: "Would you buy ...?" and pitching before you have listened.

After the call, from the founder's notes or a meeting-notes connector if one is
connected, write what you learned, the real budget and timing, and the next
step, and update the CRM.

## Step 6: the proposal

When the client asks for a price, draft the proposal in Google Drive (or
`founder/sales/proposals/`): their problem in their words, the scope, the price
from `founder/pricing.md` or the money plan (show what it includes), the
timeline, terms (deposit, cancellation, liability from the legal set-up), and
one next step. Mark it `REVIEW`: The founder approves every price. When it is
sent, move the deal to `proposal`.

## Step 7: keep the CRM true

After every interaction: add a note (what happened, who, when, one or two
sentences), set `next_step` and `next_date`, and move the stage **only with
evidence**:

| stage | the evidence |
| --- | --- |
| contacted | the first message was sent |
| meeting | the client confirmed a date and time |
| proposal | a proposal with a price was sent |
| won / lost | the client said so in writing; quote their words in the note |

If the evidence is not there, leave the stage and say so. Finish with a table:
account · stage before → after · why.

## Step 8: the weekly review

Every week (offer to schedule it), read the CRM and write
`founder/sales/review-<date>.md`:

1. The pipeline by stage and project: count, value low to high.
2. Overdue next steps, and open deals with no note for 14 days or more.
3. The three deals to push this week and the exact next action for each.
4. Won and lost since last week, with the reason in the client's words.
5. **Against the plan**: won and likely deals against the units in
   `founder/plan.json`. If sales are behind, say by how much and tell the CFO
   which year's units to lower. Never raise the plan's units from hope.

## Rules

- Nothing is sent, signed or promised without the founder's explicit OK.
- Every fact about an account has a public source; every number in a draft is
  real. No fake urgency, references or case studies.
- Simulated buyer answers from `/founder-consumer` are not leads and never go in
  the CRM.
- Give each connector only the access the task needs (reading for research,
  drafting for email).

## Output

`founder/sales/` (ICP per project, accounts, drafts, calls, proposals, weekly
reviews) and the CRM records. Next: `/founder-cfo` when the weekly review shows
the plan's units are off; `/founder-offer` when the same objection keeps coming
back.