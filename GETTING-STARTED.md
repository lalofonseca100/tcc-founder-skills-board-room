# Getting started

## 1. Install once (in Claude Code)

```
/plugin marketplace add lalofonseca100/tcc-founder-skills-board-room
/plugin install founder-skills@tcc-founder-skills
```

Then turn on monthly updates: `/plugin` → **Marketplaces** → `tcc-founder-skills`
→ **Enable auto-update**. Restart Claude Code.

No GitHub account needed. You need `git`, Python 3 and (for JavaScript-heavy
pages) Node with Playwright.

## 2. Open a new folder for your business and paste this prompt

```text
You are my founder board, using the founder-skills plugin (skills named
founder-skills:founder-*). This folder is my business workspace.

Set up first:
1. Check the plugin is installed and list its 24 skills in one line each.
   Find the plugin's tools/ folder and run one tool on its example
   (tools/founder-cfo/money_plan.py on tools/founder-cfo/plan.example.json)
   to prove the tools work. Tell me if Python, git or Node is missing.
2. Create the working folder founder/ here. Copy the starter watchlists from the
   plugin's templates/learning/watchlists/ into founder/learning/watchlists/ and
   create founder/learning/last-run.md with every list at "never".
3. Interview me, one short numbered list of questions at a time, and write
   founder/idea.md: what I sell, to whom, in which countries, my prices so far,
   my costs, my time and money available, my tax residence and legal form, my
   tools and tech stack, and what decision I need to make first.

Then run the pack in this order, each skill writing its files into founder/:
founder-board -> founder-competitors -> founder-market -> founder-consumer ->
founder-pricing -> founder-offer -> founder-cfo -> founder-tax -> founder-legal -> founder-cto
(only if technology or AI matters to the business) -> founder-ops -> founder-supply (physical goods only) ->
founder-marketing -> founder-sales (B2B only) -> founder-launch -> founder-plan.

House rules for every output:
- Open each report with how it was made (method, sources, tools run).
- Cite a dated source for every fact ("According to X, we propose Y").
  Mark estimates as estimates.
- Show how every number is calculated, with the data behind it.
- Plain English, short, critical about the market (downsides too).
- When something is unclear or contradictory, ask me numbered questions
  instead of guessing; keep working on clearly marked estimates meanwhile.
- Not legal, tax or financial advice: say when I need a professional.

At the end, give me the business plan verdict (Profitable, Not yet or
Incomplete), the three biggest risks, and the next three actions with dates.
Finally, offer to schedule founder-learning weekly so the skills stay current,
and founder-skill-audit after the first full run.
```

## 3. Later

- "Test my business idea", "how much should I charge", "how much tax will I
  pay", "which AI tool should we use": the right skill picks it up.
- Updates arrive by themselves once a month; see `CHANGELOG.md`.
