#!/usr/bin/env python3
"""Multi-year money plan: several products, yearly volumes, seasons, payment timing.

Reads a plan.json and writes a markdown report: income and costs per year, the
result per year in a base, low and high case, break-even volume, cash month by
month (with deposits and late payments), the cash needed, VAT to set aside and a
verdict. Standard library only, no network.

plan.json fields
    business          name of the business
    currency          "EUR" (default), "USD", "GBP" or any symbol
    start_year        first calendar year, e.g. 2027
    years             number of years to model (1-10)
    opening_cash      money in the bank at the start (default 0)
    vat_rate          sales VAT/BTW rate to set aside, e.g. 0.21 (optional)
    target_year       the year the result must be positive (default: last year)
    founder_hours     founder hours per year, for the result per hour (optional)
    cases             {"low": 0.6, "high": 1.3}: volume multipliers (default)
    products          list of:
        name          what one unit is ("medium festival, 1 work")
        price         price per unit before VAT, billed to the client
        variable      cost of ONE unit paid out (artist, transport, crew...)
        units         one number per year: units sold in that year
        season        optional 12 weights: share of units in each month
        deposit       optional share of the price paid before delivery (0-1)
        deposit_months_before   months before delivery the deposit arrives
        pay_months_after        months after delivery the rest arrives
        source        where the price and costs come from
    costs             list of:
        name, per_year (one number per year), source
        upfront       true: paid in month 1 of each year (insurance), else monthly
    one_off           list of {name, amount, year, month, source}: start costs
"""

import argparse
import json
import math
import sys

SYMBOLS = {"EUR": "€", "USD": "$", "GBP": "£"}


class PlanError(ValueError):
    pass


def money(v, sym):
    sign = "-" if v < 0 else ""
    return "%s%s%s" % (sign, sym, "{:,.0f}".format(abs(round(v))))


def per_year(item, field, n):
    vals = item.get(field)
    if not isinstance(vals, list) or len(vals) != n:
        raise PlanError("'%s' in '%s' needs %d numbers, one per year" % (field, item.get("name", "?"), n))
    return [float(v) for v in vals]


def load(path):
    with open(path, encoding="utf-8") as f:
        plan = json.load(f)
    n = int(plan.get("years", 0))
    if not 1 <= n <= 10:
        raise PlanError("'years' must be 1 to 10")
    if not plan.get("products"):
        raise PlanError("give at least one product")
    for p in plan["products"]:
        per_year(p, "units", n)
        s = p.get("season")
        if s is not None and (len(s) != 12 or sum(s) <= 0):
            raise PlanError("'season' in '%s' needs 12 weights" % p["name"])
    for c in plan.get("costs", []):
        per_year(c, "per_year", n)
    return plan


def analyse(plan, volume=1.0):
    n = int(plan["years"])
    y0 = int(plan["start_year"])
    years = list(range(y0, y0 + n))
    months = 12 * n
    inflow = [0.0] * months
    outflow = [0.0] * months
    billings = [0.0] * n
    income = [0.0] * n
    units_total = [0.0] * n
    rows = []
    for p in plan["products"]:
        price, var = float(p["price"]), float(p["variable"])
        units = [u * volume for u in per_year(p, "units", n)]
        season = p.get("season") or [1] * 12
        w = [float(x) / sum(season) for x in season]
        dep = float(p.get("deposit", 0))
        before = int(p.get("deposit_months_before", 0))
        after = int(p.get("pay_months_after", 0))
        for i, u in enumerate(units):
            billings[i] += u * price
            income[i] += u * (price - var)
            units_total[i] += u
            for m in range(12):
                k = 12 * i + m
                q = u * w[m]
                inflow[max(0, k - before)] += q * price * dep
                inflow[min(months - 1, k + after)] += q * price * (1 - dep)
                outflow[k] += q * var
        rows.append((p["name"], units, price - var, p.get("source", "")))
    costs = [0.0] * n
    for c in plan.get("costs", []):
        vals = per_year(c, "per_year", n)
        for i, v in enumerate(vals):
            costs[i] += v
            if c.get("upfront"):
                outflow[12 * i] += v
            else:
                for m in range(12):
                    outflow[12 * i + m] += v / 12.0
    one_off = [0.0] * n
    for o in plan.get("one_off", []):
        i = int(o.get("year", y0)) - y0
        if not 0 <= i < n:
            raise PlanError("one-off '%s' is outside the plan years" % o.get("name"))
        one_off[i] += float(o["amount"])
        outflow[12 * i + int(o.get("month", 1)) - 1] += float(o["amount"])
    result = [income[i] - costs[i] - one_off[i] for i in range(n)]
    bal, lowest, low_k, balances = float(plan.get("opening_cash", 0)), None, 0, []
    for k in range(months):
        bal += inflow[k] - outflow[k]
        balances.append(bal)
        if lowest is None or bal < lowest:
            lowest, low_k = bal, k
    # share of the planned volume (same product mix) that just covers the costs
    breakeven = [(costs[i] + one_off[i]) / income[i] if income[i] > 0 else math.inf for i in range(n)]
    return {
        "years": years, "rows": rows, "billings": billings, "income": income,
        "costs": costs, "one_off": one_off, "result": result, "units": units_total,
        "breakeven": breakeven, "balances": balances, "lowest": lowest,
        "lowest_month": (years[low_k // 12], low_k % 12 + 1),
        "cash_needed": max(0.0, -(lowest - float(plan.get("opening_cash", 0)))),
    }


def verdict(plan, a):
    target = int(plan.get("target_year", a["years"][-1]))
    i = a["years"].index(target) if target in a["years"] else len(a["years"]) - 1
    checks = [
        (a["lowest"] >= 0, "The bank balance never goes below zero (lowest %s in %d-%02d)."
         % (money(a["lowest"], "%s"), a["lowest_month"][0], a["lowest_month"][1])),
        (all(r > 0 for r in a["result"][i:]), "The result is positive from %d on." % target),
    ]
    if not any(c > 0 for _, _, c, _ in a["rows"]):
        checks.append((False, "No product earns money before fixed costs."))
    return ("Profitable" if all(ok for ok, _ in checks) else "Not yet"), checks


def report(plan, sym):
    a = analyse(plan)
    cases = plan.get("cases", {"low": 0.6, "high": 1.3})
    alt = {k: analyse(plan, float(v)) for k, v in cases.items()}
    v, checks = verdict(plan, a)
    ys = a["years"]
    head = "| | " + " | ".join(str(y) for y in ys) + " |\n|---|" + "---:|" * len(ys) + "\n"
    line = lambda label, vals, f=lambda x: money(x, sym): "| %s | %s |\n" % (label, " | ".join(f(x) for x in vals))
    out = ["# Money plan %d-%d: %s\n" % (ys[0], ys[-1], plan.get("business", "")),
           "**Verdict: %s.**\n" % v]
    out += ["- %s %s" % ("PASS" if ok else "FAIL", t.replace("%s", sym)) for ok, t in checks]
    out.append("\n## Units per year (base)\n")
    out.append("| product | " + " | ".join(str(y) for y in ys) + " | kept per unit | source |\n|---|"
               + "---:|" * (len(ys) + 1) + "---|\n")
    for name, units, keep, src in a["rows"]:
        out.append("| %s | %s | %s | %s |\n" % (name, " | ".join("{:,.1f}".format(u).rstrip("0").rstrip(".") for u in units),
                                              money(keep, sym), src))
    out.append("\n## The result\n\n" + head)
    out.append(line("Client billings", a["billings"]))
    out.append(line("Income after unit costs", a["income"]))
    out.append(line("Running costs", a["costs"]))
    out.append(line("One-off costs", a["one_off"]))
    out.append(line("**Result, base**", a["result"]))
    for k, b in alt.items():
        out.append(line("Result, %s (x%s volume)" % (k, cases[k]), b["result"]))
    out.append(line("Share of planned volume that covers costs", a["breakeven"],
                    lambda x: "never" if math.isinf(x) else "%.0f%%" % (x * 100)))
    if plan.get("founder_hours"):
        h = float(plan["founder_hours"])
        out.append(line("Result per founder-hour", [r / h for r in a["result"]], lambda x: "%s%.2f" % (sym, x)))
    out.append("\n## Cash\n\n")
    out.append("- Opening cash: %s. Lowest balance: %s in %d-%02d. Cash needed before it pays for itself: %s.\n"
               % (money(float(plan.get("opening_cash", 0)), sym), money(a["lowest"], sym),
                  a["lowest_month"][0], a["lowest_month"][1], money(a["cash_needed"], sym)))
    for k, b in alt.items():
        out.append("- %s case: lowest balance %s in %d-%02d.\n" % (k.capitalize(), money(b["lowest"], sym),
                                                                b["lowest_month"][0], b["lowest_month"][1]))
    out.append("\nBalance at the end of each month, year 1:\n\n| " + " | ".join("M%d" % m for m in range(1, 13))
               + " |\n|" + "---:|" * 12 + "\n| " + " | ".join(money(x, sym) for x in a["balances"][:12]) + " |\n")
    if plan.get("vat_rate"):
        r = float(plan["vat_rate"])
        out.append("\n## VAT to set aside\n\nPrices above exclude VAT. At %.0f%%, the VAT charged on billings is "
                   % (r * 100) + ", ".join("%d: %s" % (y, money(b * r, sym)) for y, b in zip(ys, a["billings"]))
                   + ". Most of it is paid back to the tax office each quarter, minus the VAT on your own costs; "
                   "keep it apart from the cash above.\n")
    srcs = [(c["name"], c.get("source", "")) for c in plan.get("costs", [])] + \
           [(o["name"], o.get("source", "")) for o in plan.get("one_off", [])]
    out.append("\n## Costs and their sources\n\n| cost | " + " | ".join(str(y) for y in ys) + " | source |\n|---|"
               + "---:|" * len(ys) + "---|\n")
    for c in plan.get("costs", []):
        out.append("| %s | %s | %s |\n" % (c["name"], " | ".join(money(x, sym) for x in per_year(c, "per_year", len(ys))),
                                         c.get("source", "")))
    for o in plan.get("one_off", []):
        cells = [money(float(o["amount"]), sym) if y == int(o.get("year", ys[0])) else "" for y in ys]
        out.append("| %s (one-off, month %d) | %s | %s |\n" % (o["name"], int(o.get("month", 1)), " | ".join(cells),
                                                             o.get("source", "")))
    return "".join(x if x.endswith("\n") else x + "\n" for x in out), v


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("plan", help="the business's plan.json")
    ap.add_argument("--out", help="write the report here (markdown)")
    ap.add_argument("--volume", type=float, help="what-if: multiply every volume")
    ap.add_argument("--check", action="store_true", help="print the verdict only; exit 0 if Profitable")
    args = ap.parse_args(argv)
    try:
        plan = load(args.plan)
    except (OSError, ValueError) as e:
        sys.exit("error: %s" % e)
    if args.volume:
        for p in plan["products"]:
            p["units"] = [u * args.volume for u in p["units"]]
    sym = SYMBOLS.get(plan.get("currency", "EUR"), plan.get("currency", "EUR"))
    text, v = report(plan, sym)
    if args.check:
        print(v)
        return 0 if v == "Profitable" else 1
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote %s (verdict: %s)" % (args.out, v))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
