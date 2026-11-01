# Founder skills (Board Room)

A Claude Code plugin with 17 skills that work as a founder's board and team:
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
| founder-launch | a cheap real test first, countdown, launch day, first 30 days |
| founder-cfo | unit economics and a multi-year, multi-product money plan (EUR, VAT, cash) |
| founder-tax | tax for the Netherlands, Mexico, Spain and the UAE, every rate sourced and dated |
| founder-cto | AI and tech decisions, implementation plans, relentless but polite web research |
| founder-plan | compiles everything into one business plan with a computed verdict |
| founder-learning | weekly check of each skill's watchlist; logs changes for approval |
| founder-skill-audit | scores every skill on 9 criteria and finds missing ones |

## Install (Claude Code)

Needs Claude Code, `git`, Python 3, and Node (only for `render_fetch.js`).

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

## Keeping current

`founder-learning` re-reads each skill's watchlist (`founder/learning/watchlists/`)
on its cadence and writes what changed to `founder/learning/changelog-YYYY-MM.md`.
Nothing changes in a skill without your approval. Schedule it weekly if you can.

## Limits

Not legal, tax or financial advice. Tax rates and AI prices move: check the
dates in each source before acting.

## Credits

Built on [founder-skill](https://github.com/Jakeschincariol/founder-skill) by
Jake Schincariol (MIT). founder-sales adapts ideas from
`hiveflowai/claude-para-revenue` (MIT, Jonathan Olvera). See `LICENSE`.
