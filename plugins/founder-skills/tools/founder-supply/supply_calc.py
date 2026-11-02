#!/usr/bin/env python3
"""supply_calc.py - procurement, trade and logistics numbers, step by step (stdlib only, no network).

Every result prints how it was derived and which rule (with source id from rules.json) it used,
so a report can show the working. Duty and VAT rates are inputs per case, taken from the official
tariff for the HS code (EU TARIC, MX TIGIE, GCC tariff), never from this tool.

Usage:
  python3 -I supply_calc.py case.json [--rules rules.json] [--out result.md]
case.json: {"cases": [ {"type": ..., ...}, ... ]}  (see case.example.json)

Case types:
  landed_cost : goods_value, currency, incoterm, dest (EU|MX|AE), freight, insurance, duty_rate,
                vat_rate, other_import_fees, broker_fee, inland_delivery, units, [fx_to_eur],
                [duty_source], [vat_source], [vat_recoverable]
  scorecard   : criteria {name: weight}, suppliers [{name, scores {criterion: 0-5}, [country]}]
  inventory   : annual_demand, order_cost, unit_cost, holding_rate, lead_time_days,
                [daily_demand_sd], [service_level]
  route       : region (EU|MX), legs [{name, km, avg_kmh, [tolls]}], fuel_l_per_100km, fuel_price,
                driver_cost_per_h, [other_per_km], [load_units]
Not legal, customs or tax advice: a customs broker (douane-expediteur / agente aduanal) checks
before goods move.
"""
import argparse, json, math, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def eur(x):
    return f"{x:,.2f}"


def landed_cost(c, R):
    out, warn = [], []
    term = c["incoterm"].upper()
    t = R["incoterms_2020"].get(term)
    if not t:
        sys.exit(f"Unknown Incoterm {term}. Use one of the 11 Incoterms 2020 rules.")
    seller = set(t["seller_pays"])
    dest = c["dest"].upper()
    basis = R["customs_value_basis"][dest]
    fx = c.get("fx_to_eur", 1.0)
    cur = c.get("currency", "EUR")
    goods, freight, ins = c["goods_value"], c.get("freight", 0), c.get("insurance", 0)
    out.append(("Incoterm", term, f"risk passes {t['risk_passes']}; seller pays: {', '.join(sorted(seller)) or 'nothing beyond goods'}", "ICC-INCOTERMS-2020"))
    if not t["any_mode"]:
        warn.append(f"{term} is a sea/inland-waterway rule only; for containers or road/air use FCA/CPT/CIP instead.")
    # buyer's extra costs: those not included in the seller's price
    buyer_freight = 0 if "main_carriage" in seller else freight
    buyer_ins = 0 if ("insurance" in seller or term[0] == "D") else ins  # D rules: seller carries the risk to destination
    customs_value = goods + freight + ins  # CIF basis (freight/insurance to the border, whoever pays)
    out.append(("Customs value", eur(customs_value), f"{basis['basis']} = goods {eur(goods)} + freight {eur(freight)} + insurance {eur(ins)}", basis["source"]))
    duty = customs_value * c.get("duty_rate", 0)
    out.append(("Import duty", eur(duty), f"customs value x {c.get('duty_rate', 0):.2%}", c.get("duty_source", "INPUT: no source given")))
    if "duty_source" not in c:
        warn.append("duty_rate has no source: look it up per HS code in the official tariff.")
    fees = c.get("other_import_fees", 0)
    vat_base = customs_value + duty + fees
    vat = vat_base * c.get("vat_rate", 0)
    out.append(("Import VAT/IVA", eur(vat), f"(customs value + duty + other fees {eur(fees)}) x {c.get('vat_rate', 0):.2%}", c.get("vat_source", "INPUT: no source given")))
    duty_vat_by_seller = "import_duty_vat" in seller
    broker, inland = c.get("broker_fee", 0), (0 if "delivery_to_door" in seller else c.get("inland_delivery", 0))
    vat_cost = 0 if c.get("vat_recoverable", True) else vat
    if duty_vat_by_seller:
        total = goods + inland
        out.append(("Duty and VAT", "in price", "DDP: seller pays import duty and VAT", "ICC-INCOTERMS-2020"))
        warn.append("DDP into the EU or MX means the foreign seller must be able to act as importer (EORI / padrón de importadores): confirm it can.")
    else:
        total = goods + buyer_freight + buyer_ins + duty + fees + broker + inland + vat_cost
    out.append(("Landed cost", eur(total), f"goods + buyer freight {eur(buyer_freight)} + buyer insurance {eur(buyer_ins)} + duty + fees + broker {eur(broker)} + inland {eur(inland)} + VAT not recovered {eur(vat_cost)}", "calc"))
    out.append(("Cash out at import", eur(duty + fees + vat + broker if not duty_vat_by_seller else 0), "duty + fees + VAT + broker, paid before release (VAT comes back later only if recoverable)", "calc"))
    units = c.get("units", 1)
    out.append(("Per unit", eur(total / units), f"landed cost / {units} units ({cur})", "calc"))
    if fx != 1.0:
        out.append(("Per unit in EUR", eur(total / units * fx), f"x fx {fx} (state the date of the rate)", c.get("fx_source", "INPUT")))
    return out, warn


def scorecard(c, R):
    out, warn = [], []
    w = c["criteria"]
    tw = sum(w.values())
    if abs(tw - 1) > 1e-6:
        warn.append(f"Weights add to {tw:.2f}; normalised to 1.")
    rows = []
    for s in c["suppliers"]:
        missing = [k for k in w if k not in s["scores"]]
        if missing:
            warn.append(f"{s['name']}: no score for {', '.join(missing)} (counted as 0).")
        tot = sum(w[k] / tw * s["scores"].get(k, 0) for k in w)
        rows.append((tot, s))
    rows.sort(key=lambda r: -r[0])
    for i, (tot, s) in enumerate(rows, 1):
        detail = ", ".join(f"{k} {s['scores'].get(k, 0)}x{w[k] / tw:.2f}" for k in w)
        out.append((f"#{i} {s['name']}", f"{tot:.2f} / 5", detail, "weighted score"))
    if len(rows) < 2:
        warn.append("Only one supplier: single-source risk. Scout at least one backup.")
    elif rows[0][0] - rows[1][0] < 0.25:
        warn.append("Top two are within 0.25: decide on a quote, a sample or a reference call, not on the score.")
    return out, warn


def inventory(c, R):
    out, warn = [], []
    D, S, P, h = c["annual_demand"], c["order_cost"], c["unit_cost"], c["holding_rate"]
    H = P * h
    eoq = math.sqrt(2 * D * S / H)
    out.append(("EOQ", f"{eoq:,.0f} units", f"sqrt(2 x demand {D} x order cost {S} / holding {eur(H)} per unit-year)", "Harris 1913"))
    d = D / 365
    L = c["lead_time_days"]
    sd = c.get("daily_demand_sd", 0)
    sl = c.get("service_level", 0.95)
    z = statistics.NormalDist().inv_cdf(sl)
    ss = z * sd * math.sqrt(L)
    out.append(("Safety stock", f"{ss:,.0f} units", f"z {z:.2f} (service {sl:.0%}) x daily sd {sd} x sqrt(lead time {L} d)", "standard formula"))
    out.append(("Reorder point", f"{d * L + ss:,.0f} units", f"daily demand {d:.1f} x {L} d + safety stock", "calc"))
    out.append(("Orders per year", f"{D / eoq:.1f}", "demand / EOQ", "calc"))
    out.append(("Yearly cost", eur(D / eoq * S + (eoq / 2 + ss) * H), "ordering + holding (cycle stock/2 + safety stock)", "calc"))
    if sd == 0:
        warn.append("No demand variability given: safety stock is 0. Use real sales data or a stated estimate.")
    return out, warn


def route(c, R):
    out, warn = [], []
    reg = c["region"].upper()
    rules = R["driving"][reg]
    if rules["status"] != "law":
        warn.append(f"{reg} driving rules are '{rules['status']}': {rules.get('_check', 'confirm before use')}")
    km = sum(l["km"] for l in c["legs"])
    drive = sum(l["km"] / l["avg_kmh"] for l in c["legs"])
    tolls = sum(l.get("tolls", 0) for l in c["legs"])
    breaks = max(0, math.ceil(drive / rules["max_drive_before_break_h"]) - 1) * rules["break_h"]
    days = max(1, math.ceil(drive / rules["max_daily_drive_h"]))
    rests = (days - 1) * rules["daily_rest_h"]
    elapsed = drive + breaks + rests
    out.append(("Distance", f"{km:,.0f} km", " + ".join(f"{l['name']} {l['km']}" for l in c["legs"]), "INPUT"))
    out.append(("Driving time", f"{drive:.1f} h", "sum of km / average speed per leg", "calc"))
    out.append(("Breaks and rests", f"{breaks + rests:.1f} h", f"{breaks:.2f} h breaks (one {rules['break_h']} h per {rules['max_drive_before_break_h']} h) + {days - 1} daily rest(s) of {rules['daily_rest_h']} h", rules["source"]))
    out.append(("Door to door", f"{elapsed:.1f} h", f"{days} driving day(s) at max {rules['max_daily_drive_h']} h/day", rules["source"]))
    fuel = km * c["fuel_l_per_100km"] / 100 * c["fuel_price"]
    driver = (drive + breaks) * c["driver_cost_per_h"]
    other = km * c.get("other_per_km", 0)
    total = fuel + driver + tolls + other
    out.append(("Fuel", eur(fuel), f"{km:,.0f} km x {c['fuel_l_per_100km']} l/100 km x {c['fuel_price']}", c.get("fuel_source", "INPUT")))
    out.append(("Driver", eur(driver), f"(driving + breaks) {drive + breaks:.1f} h x {c['driver_cost_per_h']}/h (rest time paid? check contract)", "INPUT"))
    out.append(("Tolls + other", eur(tolls + other), f"tolls {eur(tolls)} + {c.get('other_per_km', 0)}/km (wear, insurance, truck)", c.get("tolls_source", "INPUT")))
    out.append(("Trip cost", eur(total), f"{eur(total / km)} per km", "calc"))
    if c.get("load_units"):
        out.append(("Per unit carried", eur(total / c["load_units"]), f"/ {c['load_units']} units", "calc"))
    if drive > rules["max_daily_drive_h"] and days == 1:
        warn.append("Over the daily driving limit: plan a second driver or an overnight stop.")
    return out, warn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--rules", default=os.path.join(HERE, "rules.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    R = json.load(open(a.rules))
    cases = json.load(open(a.case))["cases"]
    fn = {"landed_cost": landed_cost, "scorecard": scorecard, "inventory": inventory, "route": route}
    md = ["# Supply calculations", "", "Not legal, customs or tax advice. A customs broker checks before goods move.", ""]
    for c in cases:
        if c["type"] not in fn:
            sys.exit(f"Unknown case type {c['type']}")
        rows, warn = fn[c["type"]](c, R)
        md += [f"## {c.get('name', c['type'])} ({c['type']})", "", "| step | result | how | source |", "| --- | --- | --- | --- |"]
        md += [f"| {s} | {r} | {h} | {src} |" for s, r, h, src in rows]
        if warn:
            md += ["", "Warnings:"] + [f"- {w}" for w in warn]
        md.append("")
    text = "\n".join(md)
    if a.out:
        open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
