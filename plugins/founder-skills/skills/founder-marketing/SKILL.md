---
name: "founder-marketing"
description: "Your marketing director: positioning, the channels your buyers use, a dated 30-day launch campaign, ten hooks, budget and the max you can pay per customer. Use for 'marketing plan' or 'how do I get customers'."
---

# founder-marketing

A business no one hears about does not exist. This skill plans how the first
customers hear about it, using what the rest of the pack already learned instead
of a generic playbook.

## Step 1: read the evidence

- `founder/panel/results.md`: who buys, who doesn't, and why. The segments with the
  highest buy rate are the first audience. The top objections are what the
  marketing must answer.
- `founder/competitors.md`: how competitors position themselves (so you do not
  sound like them) and the gap.
- `founder/offer.md` and `founder/pricing.md`: what is being sold, at what price.
- `founder/numbers.json`: what a customer is worth, which caps what you can spend to
  win one.

If none of these exist, say what is missing and offer to run `/founder-consumer
--quick` first. Do not invent an audience.

## Step 2: positioning

One line, then the reasons:

```
For <the segment that buys most>, who <their problem in their words>,
<business> is the <category> that <the gap>, unlike <the nearest alternative>.
```

Give three versions, recommend one, and say which panel evidence supports it.

## Step 3: channels

List where the first audience actually spends attention, specific to the business
type and place: foot traffic and window signage, Google Maps, Instagram and TikTok,
local creators, neighbourhood groups, partnerships with nearby businesses, email,
paid search, paid social. For each: why it fits this buyer, rough cost, and how you
will know it worked. Pick two or three to start; say what you are not doing and why.

## Step 4: the 30-day campaign

`founder/marketing.md` gets a dated calendar from launch minus 14 days to launch
plus 16: what goes out each day, on which channel, with the message. Include:

- **Ten hooks**, each answering one panel objection or using one buyer reason,
  written for the format (a 3-second opening line for video, a headline for an ad,
  a sign in the window).
- The launch-week offer from `founder/pricing.md` and when it ends.
- What to post when there is nothing new to say (behind the scenes, the making of).

## Step 5: budget and numbers

- The budget split across the chosen channels.
- The most you can pay to win a customer: from the CFO's contribution per unit and
  the panel's purchases per buyer, show the sum.
- The three numbers to watch weekly and the level that means "change something".

## Rules

- No fake reviews, follower counts, testimonials, before/afters or "as seen on".
- Panel quotes are research; never use them as customer quotes in ads.
- Disclose paid partnerships. Follow the advertising rules for claims in the user's
  market (health and earnings claims especially). Not legal advice.

## Output

`founder/marketing.md`. Next: `/founder-brand`, then `/founder-launch`.

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
