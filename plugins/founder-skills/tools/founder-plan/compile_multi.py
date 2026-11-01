#!/usr/bin/env python3
"""Compile the business plan for a multi-year business (founder/plan.json).

Same sections as compile.py, plus the market and the money plan, but the verdict
and the key numbers come from founder-cfo/money_plan.py: the bank balance never
goes below zero, and the result is positive from the target year on. The
simulated buyer panel is reported, not used as a pass/fail check.

    python3 compile_multi.py --dir founder            # writes founder/business-plan.md
    python3 compile_multi.py --dir founder --check    # verdict only; exit 0 if Profitable
"""

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


compile_ = _load("founder_compile", "compile.py")
mp = _load("founder_money_plan", os.path.join("..", "founder-cfo", "money_plan.py"))

SECTIONS = list(compile_.SECTIONS)
SECTIONS.insert(2, ("market.md", "The market", "founder-market"))
SECTIONS.insert(SECTIONS.index(("cfo.md", "The numbers", "founder-cfo")) + 1,
                ("money-plan.md", "Money plan, year by year", "founder-cfo"))


def build(d):
    plan = mp.load(os.path.join(d, "plan.json"))
    sym = mp.SYMBOLS.get(plan.get("currency", "EUR"), plan.get("currency", "EUR"))
    a = mp.analyse(plan)
    v, checks = mp.verdict(plan, a)
    idea = compile_._read(os.path.join(d, "idea.md"))
    title = plan.get("business") or "Your business"
    if idea and idea.splitlines()[0].startswith("# "):
        title = idea.splitlines()[0][2:].strip()
    L = ["# %s · Business plan" % title, "", "**Verdict: %s**" % v, ""]
    L += ["- %s %s" % ("✓" if ok else "✗", t.replace("%s", sym)) for ok, t in checks]
    ys = a["years"]
    L += ["", "| key number | " + " | ".join(str(y) for y in ys) + " |", "| --- |" + " ---: |" * len(ys),
          "| Client billings | " + " | ".join(mp.money(x, sym) for x in a["billings"]) + " |",
          "| Result, base | " + " | ".join(mp.money(x, sym) for x in a["result"]) + " |",
          "", "Cash needed before it pays for itself: %s (lowest balance in %d-%02d)."
          % (mp.money(a["cash_needed"], sym), a["lowest_month"][0], a["lowest_month"][1])]
    raw = compile_._read(os.path.join(d, "panel", "results.json"))
    if raw:
        p = json.loads(raw)
        L.append("Simulated buyer panel: %d buy · %d pass (objections only; not a sales forecast)."
                 % (p["buys"], p["passes"]))
    L.append("")
    if idea:
        L += ["## The idea", "", compile_._strip_h1(idea), ""]
    missing = []
    for fname, heading, skill in SECTIONS:
        text = compile_._read(os.path.join(d, fname))
        if text:
            L += ["## %s" % heading, "", compile_._strip_h1(text), ""]
        else:
            missing.append((heading, skill))
    if missing:
        L += ["## Not done yet", ""] + ["- %s: run /%s" % m for m in missing] + [""]
    L.append("_The panel is simulated buyers and the numbers are projections from your inputs. Confirm demand with real"
             " customers and costs with real quotes before you spend. Not financial, legal or tax advice._")
    return v, "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default="founder")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", help="default: <dir>/business-plan.md")
    args = ap.parse_args(argv)
    try:
        v, text = build(args.dir)
    except (OSError, ValueError) as e:
        sys.exit("error: %s (run /founder-cfo to write founder/plan.json)" % e)
    if args.check:
        print(v)
        return 0 if v == "Profitable" else 1
    out = args.out or os.path.join(args.dir, "business-plan.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote %s (verdict: %s)" % (out, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
