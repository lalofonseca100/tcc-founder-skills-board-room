# Founder skills (Board Room)

A Claude Code plugin with 24 skills that work as a founder's board and team:
test an idea, size the market, price it, plan the money and the taxes, choose
the tech, sell, launch, and keep everything current.

| skill | what it does |
| --- | --- |
| founder-board | three lenses score an idea, name what would kill it and vote |
| founder-competitors | competitors and substitutes from public sources, every fact linked |
| founder-market | market size bottom-up and top-down (total, reachable, winnable) |
| founder-consumer | simulated buyer panel: who buys, who passes, why, price answers |
| founder-pricing | Van Westendorp price range, ladder and opening offer |
| founder-offer | an offer with honest bonuses, guarantee and urgency |
| founder-brand | names with trademark/domain checks, voice and taglines |
| founder-marketing | positioning, channels, 30-day campaign, max cost per customer |
| founder-sales | B2B ideal client, target list, outreach drafts, pipeline in a CRM |
| founder-ops | suppliers, staffing, routines, permits, risk register |
| founder-supply | procurement, suppliers, landed cost, Incoterms, customs, routes, warehousing |
| founder-launch | a cheap real test first, countdown, launch day, first 30 days |
| founder-cfo | unit economics and a multi-year, multi-product money plan (EUR, VAT, cash) |
| founder-tax | tax for the Netherlands, Mexico, Spain and the UAE, every rate sourced and dated |
| founder-legal | reads, drafts and benchmarks contracts (international, EU, NL, Spain, Mexico, US/Texas), risk score, win-win terms, lawyer gates |
| founder-cto | AI and tech decisions, implementation plans, relentless but polite web research |
| founder-engineering | CTO office, external: reviews the code your dev team or agents build (bugs, code security, tech debt, DORA delivery metrics, estimates), read and comment only |
| founder-cio | CTO office, internal: one inventory of tools and costs, accounts and access, cybersecurity basics (CIS IG1, NIST CSF 2.0), GDPR records, tool ROI |
| founder-human-development | Human Development office: a direct, Socratic coach for the founder's growth and for leading teams and clients the Conscious Business way (Kofman, Carnegie, Ferriss, NVC); coaching, not therapy, with privacy and crisis limits |
| founder-research | R&D: reads videos (captions and key frames), papers, courses and pages, grades each source, turns insights into skill updates |
| founder-chief-of-staff | connects all skills: routes findings, decision log, idea parking lot, one weekly brief |
| founder-plan | compiles everything into one business plan with a computed verdict |
| founder-learning | weekly check of each skill's watchlist; logs changes for approval |
| founder-skill-audit | scores every skill on 9 criteria and finds missing ones |

## Install (Claude Code)

Needs Claude Code, `git`, Python 3, and Node (only for `render_fetch.js`). founder-research's video tools also use `ffmpeg`, `pdftotext` (poppler) and `yt-dlp`.

```
/plugin marketplace add lalofonseca100/tcc-founder-skills-board-room
/plugin install founder-skills@tcc-founder-skills
```

Skills then show up as `founder-skills:founder-cfo` and so on. Type
`/founder-skills:founder-board` or just ask ("test my business idea").

New here? Read [GETTING-STARTED.md](GETTING-STARTED.md): install, then one prompt to start.

## Automatic updates (recommended)

A new version is published once a month. To receive it without doing anything,
turn on auto-update for this marketplace, in either way:

- In Claude Code: `/plugin` → **Marketplaces** → `tcc-founder-skills` →
  **Enable auto-update**.
- Or add this to `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "tcc-founder-skills": {
      "source": { "source": "github", "repo": "lalofonseca100/tcc-founder-skills-board-room" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "founder-skills@tcc-founder-skills": true }
}
```

Claude Code checks for updates when it starts. To update by hand:
`/plugin marketplace update tcc-founder-skills`. What changed is in `CHANGELOG.md`.

## Tools

`plugins/founder-skills/tools/` holds the scripts the skills run (Python 3
standard library; `render_fetch.js` needs Node and Playwright). The skills find
them as the `tools/` folder of the plugin, or at `$FOUNDER_TOOLS` if you set it.

## Working folder

Skills read and write a `founder/` folder in your current project
(`founder/idea.md`, `founder/plan.json`, `founder/learning/`...). Keep one per business.

## Token budget

Every skill ends with the same *Token budget* section, so the pack stays cheap
to run: lite output first (full report, deck or Word file only on request or for
the final version), read only what the task needs, mechanical steps on small
models (`haiku`/`sonnet` sub-agents), small swarms first, no recurring run
without your OK, short threads with one-page handoffs, small edits instead of
rebuilds. Long skills keep their core in `SKILL.md` and detail in a
`reference.md` read only when needed. `founder-chief-of-staff` is the token
steward: a *Consumo* line in the weekly brief and a monthly efficiency check
(Mode 7). `founder-skill-audit` scores token efficiency as criterion 10.

## Keeping current

`founder-learning` re-reads each skill's watchlist (`founder/learning/watchlists/`)
on its cadence and writes what changed to `founder/learning/changelog-YYYY-MM.md`.
Nothing changes in a skill without your approval. Schedule it every two weeks,
in the same run as `founder-research`.

## Limits

Not legal, tax or financial advice. Tax rates and AI prices move: check the
dates in each source before acting.

## Credits

Built on [founder-skill](https://github.com/Jakeschincariol/founder-skill) by
Jake Schincariol (MIT). founder-sales adapts ideas from
`hiveflowai/claude-para-revenue` (MIT, Jonathan Olvera). See `LICENSE`.
