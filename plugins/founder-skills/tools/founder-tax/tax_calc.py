#!/usr/bin/env python3
"""tax_calc.py - Netherlands and Mexico tax for small businesses, step by step (stdlib only, no network).

Every step prints the rule, the number and the source id from rules.json, so a report can show
how each figure was derived. Values marked unverified/proposal are flagged in the output.

Usage:
  python3 -I tax_calc.py case.json [--rules rules.json] [--out result.md]
case.json: {"cases": [ {...}, ... ]}  (see case.example.json)

Regimes:
  NL eenmanszaak : profit, turnover, urencriterium (bool), starter (bool)
  NL bv          : profit (before DGA salary), dga_salary (default gebruikelijk loon), distribute (bool)
  MX resico_pf   : income (collected, before IVA)
  MX pf_empresarial : income, deductions (actividad empresarial / servicios profesionales, art. 152)
  MX pm          : profit (resultado fiscal), distribute (bool)
Not tax advice: check the result with an accountant before money moves.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


class Calc:
    def __init__(self, rules, country, year):
        self.r = rules[country]
        self.country, self.year = country, str(year)
        if self.year not in self.r:
            sys.exit(f"No {country} rules for {year}. Known: {sorted(k for k in self.r)}")
        self.lines, self.warn = [], []
        st = self.r[self.year].get("status")
        if st != "law":
            self.warn.append(f"{country} {year} rules have status '{st}': not law yet.")

    def p(self, key):
        """Get a parameter for the year, falling back to the previous year with a warning."""
        y = self.r[self.year]
        if key in y:
            v = y[key]
        else:
            prev = str(int(self.year) - 1)
            if prev not in self.r or key not in self.r[prev]:
                sys.exit(f"Missing parameter {key} for {self.country} {self.year}")
            v = self.r[prev][key]
            self.warn.append(f"{key}: no {self.year} value, used {prev} ({v.get('src')}).")
            return v
        if isinstance(v, dict) and v.get("status") == "unverified":
            self.warn.append(f"{key}: unverified ({v.get('src')}). {v.get('note', '')}".strip())
        return v

    def sub(self, key, field):
        """A field of a parameter, with fallback to last year if this year's entry lacks it."""
        v = self.p(key)
        if field in v:
            return v[field], v.get("src")
        prev = str(int(self.year) - 1)
        pv = self.r.get(prev, {}).get(key, {})
        if field in pv:
            self.warn.append(f"{key}.{field}: no {self.year} value, used {prev}.")
            return pv[field], pv.get("src")
        sys.exit(f"Missing {key}.{field}")

    def step(self, label, value, rule, src=""):
        self.lines.append((label, value, rule, src or ""))
        return value


def bracket_tax(amount, brackets):
    tax, low = 0.0, 0.0
    for top, rate in brackets:
        hi = amount if top is None else min(amount, top)
        if hi > low:
            tax += (hi - low) * rate
        if top is None or amount <= top:
            break
        low = top
    return tax


def fmt(x):
    return f"{x:,.0f}" if isinstance(x, (int, float)) else str(x)


# ---------------- Netherlands ----------------

def piecewise(x, table):
    row = [t for t in table if x >= t[0]][-1]
    return max(0.0, row[1] + (x - row[0]) * row[2]), row


def credit(c, key, x, label):
    v = c.p(key)
    if "table" in v:
        amt, row = piecewise(x, v["table"])
        return c.step(label, amt, f"{fmt(row[1])} {'+' if row[2] >= 0 else '-'} {abs(row[2]):.3%} x (income - {fmt(row[0])})", v["src"])
    prev = c.r[str(int(c.year) - 1)][key]
    amt, row = piecewise(x, prev["table"])
    c.warn.append(f"{key}: {c.year} bands not loaded; used {int(c.year) - 1} table (new max {fmt(v['max'])} not applied, small under-estimate).")
    return c.step(label, amt, f"{int(c.year) - 1} table", prev["src"])


def nl_kortingen(c, income, arbeidsinkomen, tax):
    ahk = credit(c, "algemene_heffingskorting", income, "Algemene heffingskorting")
    ak = credit(c, "arbeidskorting", arbeidsinkomen, "Arbeidskorting")
    return c.step("Kortingen used (cannot exceed tax)", min(tax, ahk + ak), "min(tax, AHK + AK)")


def nl_eenmanszaak(c, case):
    profit = case["profit"]
    c.step("Profit (winst)", profit, "input")
    za = c.p("zelfstandigenaftrek")["value"] if case.get("urencriterium", True) else 0
    hrs = c.p("urencriterium_hours")["value"]
    c.step("Zelfstandigenaftrek", -za, f"needs {hrs} hours/year" if za else "urencriterium not met", c.p("zelfstandigenaftrek")["src"])
    sa = c.p("startersaftrek")["value"] if (case.get("starter") and case.get("urencriterium", True)) else 0
    c.step("Startersaftrek", -sa, "starter + urencriterium" if sa else "not applied", c.p("startersaftrek")["src"])
    after = max(0.0, profit - za - sa)
    mkb = c.p("mkb_winstvrijstelling")
    vr = c.step("MKB-winstvrijstelling", -after * mkb["value"], f"{mkb['value']:.2%} of profit after aftrek", mkb["src"])
    taxable = c.step("Taxable profit box 1", after + vr, "profit - aftrek - MKB")
    b1 = c.p("box1_below_aow")
    tax = c.step("Box 1 tax before kortingen", bracket_tax(taxable, b1["brackets"]), "brackets " + ", ".join(f"{fmt(t) if t else 'rest'} @ {r:.2%}" for t, r in b1["brackets"]), b1["src"])
    k = nl_kortingen(c, taxable, taxable, tax)
    ib = c.step("Income tax to pay (IB)", tax - k, "tax - kortingen")
    zr, zsrc = c.sub("zvw_ondernemer", "rate")
    zmax, _ = c.sub("zvw_ondernemer", "max_income")
    zvw = c.step("Zvw bijdrage", min(taxable, zmax) * zr, f"{zr:.2%} up to {fmt(zmax)}", zsrc)
    total = ib + zvw
    c.step("TOTAL tax + Zvw", total, f"effective {total / profit:.1%} of profit" if profit else "")
    c.step("Net income", profit - total, "profit - total")
    turnover = case.get("turnover")
    if turnover is not None:
        kor = c.p("kor_threshold")["value"]
        b = c.p("btw")
        c.step("BTW", "KOR possible (no BTW)" if turnover < kor else f"charge {b['standard']:.0%}; collected BTW is not income",
               f"KOR if turnover < {fmt(kor)}", b["src"])
    return profit - total


def nl_bv(c, case):
    profit = case["profit"]
    gl = c.p("gebruikelijk_loon_dga")["value"]
    sal = min(case.get("dga_salary", gl), profit)
    c.step("BV profit before DGA salary", profit, "input")
    if sal < gl:
        c.warn.append(f"DGA salary {fmt(sal)} is below gebruikelijk loon {fmt(gl)}; only allowed with a reason the Belastingdienst accepts.")
    zr, _ = c.sub("zvw_employer", "rate")
    zmax, _ = c.sub("zvw_employer", "max_income")
    emp_zvw = min(sal, zmax) * zr
    c.step("DGA salary", sal, f"gebruikelijk loon {fmt(gl)}", c.p("gebruikelijk_loon_dga")["src"])
    c.step("Employer Zvw on salary", emp_zvw, f"{zr:.2%} up to {fmt(zmax)}")
    vpb_base = max(0.0, profit - sal - emp_zvw)
    v = c.p("vpb")
    vpb = c.step("Vpb", bracket_tax(vpb_base, v["brackets"]), f"on {fmt(vpb_base)}", v["src"])
    b1 = c.p("box1_below_aow")
    t = bracket_tax(sal, b1["brackets"])
    c.step("Box 1 tax on salary before kortingen", t, "box 1 brackets", b1["src"])
    k = nl_kortingen(c, sal, sal, t)
    loonb = c.step("Loonheffing on salary", t - k, "tax - kortingen")
    div_tax = 0.0
    left = vpb_base - vpb
    if case.get("distribute", True):
        b2 = c.p("box2")
        div_tax = c.step("Box 2 on dividend", bracket_tax(left, b2["brackets"]), f"dividend {fmt(left)} (dividend tax 15% is credited)", b2["src"])
    total = emp_zvw + vpb + loonb + div_tax
    c.step("TOTAL tax", total, f"effective {total / profit:.1%} of profit" if profit else "")
    net = profit - total - (0 if case.get("distribute", True) else left)
    c.step("Net to founder", net, "salary + dividend - tax" if case.get("distribute", True) else "salary only; rest stays in BV")
    c.warn.append("BV: add one-off and yearly BV costs (notary, accountant, payroll ~€1,500-3,500/yr) before comparing; estimate, check quotes.")
    return net


# ---------------- Mexico ----------------

def mx_resico_pf(c, case):
    inc = case["income"]
    r = c.p("resico_pf")
    c.step("Income collected (before IVA)", inc, "input")
    if inc > r["cap"]:
        c.warn.append(f"Income {fmt(inc)} is above the RESICO cap {fmt(r['cap'])}: you leave RESICO.")
    rate = next((rt for top, rt in r["tiers"] if inc <= top), r["tiers"][-1][1])
    isr = c.step("ISR RESICO", inc * rate, f"{rate:.2%} on ALL income (single rate for the tier, no deductions)", r["src"])
    costs = case.get("costs", 0)
    c.step("Business costs", -costs, "input (paid, but NOT deductible in RESICO)")
    c.step("Net", inc - costs - isr, f"effective ISR {isr / inc:.1%} of income" if inc else "")
    iva = c.p("iva")
    c.step("IVA", f"charge {iva['standard']:.0%}; IVA collected minus IVA paid goes to SAT monthly", "", iva["src"])
    c.warn.append("RESICO: companies (personas morales) paying you withhold 1.25% ISR; it is credited, not extra tax.")
    return inc - costs - isr


def mx_pf_empresarial(c, case):
    inc, ded = case["income"], case.get("deductions", 0)
    c.step("Income", inc, "input")
    c.step("Deductions", -ded, "input (must be 'estrictamente indispensables' with CFDI)")
    base = max(0.0, inc - ded)
    t = c.p("isr_pf_annual_art152")
    row = [x for x in t["rows"] if base >= x[0]][-1]
    isr = row[1] + (base - row[0]) * row[2]
    c.step("ISR art. 152", isr, f"cuota fija {fmt(row[1])} + {row[2]:.2%} over {fmt(row[0])}", t["src"])
    c.step("Net", inc - ded - isr, f"effective {isr / base:.1%} of base" if base else "")
    return inc - ded - isr


def mx_pm(c, case):
    pr = case["profit"]
    rate = c.p("isr_pm")["value"]
    isr = c.step("ISR persona moral", pr * rate, f"{rate:.0%} of resultado fiscal", c.p("isr_pm")["src"])
    left = pr - isr
    extra = 0.0
    if case.get("distribute", True):
        d = c.p("dividend_additional_pf_or_foreign")["value"]
        extra = c.step("Additional ISR on dividend", left * d, f"{d:.0%} withheld on dividend to individual or foreign resident (treaty may lower for NL)")
    c.step("Net to owner", left - extra, "")
    c.warn.append("PTU (10% profit sharing with employees) applies if the company has employees; not included.")
    return left - extra


REGIMES = {("NL", "eenmanszaak"): nl_eenmanszaak, ("NL", "bv"): nl_bv,
           ("MX", "resico_pf"): mx_resico_pf, ("MX", "pf_empresarial"): mx_pf_empresarial, ("MX", "pm"): mx_pm}

# ---------------- Spain ----------------

def es_autonomo(c, case):
    inc, exp = case["income"], case.get("expenses", 0)
    c.step("Income (before IVA)", inc, "input")
    c.step("Deductible expenses", -exp, "input (with invoices)")
    reta = c.p("reta")
    pre = max(0.0, inc - exp)
    monthly = pre * (1 - reta["gastos_genericos"]) / 12
    base = next(b for top, b in reta["tramos"] if top is None or monthly <= top)
    if case.get("new_autonomo"):
        cuota = reta["tarifa_plana_month"] * 12
        rule = f"tarifa plana {reta['tarifa_plana_month']}/month x 12 (first {reta['tarifa_plana_months']} months)"
    else:
        cuota = base * reta["rate_total"] * 12
        rule = f"monthly net {fmt(monthly)} (after {reta['gastos_genericos']:.0%} gastos genéricos) -> base mínima {base:,.2f} x {reta['rate_total']:.1%} x 12"
    c.step("Cuota autónomos (RETA)", -cuota, rule, reta["src"])
    rn = max(0.0, pre - cuota)
    g = c.p("gastos_dificil_justificacion")
    gdj = min(rn * g["rate"], g["cap"])
    c.step("Gastos de difícil justificación", -gdj, f"{g['rate']:.0%} capped at {fmt(g['cap'])} (estimación directa simplificada)", g["src"])
    bl = c.step("Base liquidable general", rn - gdj, "rendimiento neto")
    st, au = c.p("irpf_state"), c.p("irpf_baleares")
    mp = c.p("minimo_personal")
    t_state = max(0.0, bracket_tax(bl, st["brackets"]) - bracket_tax(mp["state"], st["brackets"]))
    t_au = max(0.0, bracket_tax(bl, au["brackets"]) - bracket_tax(mp["baleares"], au["brackets"]))
    c.step("IRPF state part", t_state, f"state scale minus tax on mínimo personal {fmt(mp['state'])}", st["src"])
    c.step("IRPF Baleares part", t_au, f"Baleares scale minus tax on mínimo {fmt(mp['baleares'])}", au["src"])
    irpf = t_state + t_au
    total = irpf + cuota
    c.step("TOTAL IRPF + RETA", total, f"effective {total / pre:.1%} of profit" if pre else "")
    c.step("Net", pre - total, "income - expenses - RETA - IRPF")
    c.warn.append("Spain: reducción por rendimientos bajos (art. 32.2 LIRPF) and family minimums not modelled; withholdings (15%, 7% new) and modelo 130 (20%) are advances, not extra tax.")
    iva = c.p("iva")
    c.step("IVA", f"charge {iva['standard']:.0%}; quarterly modelo 303", "", iva["src"])
    return pre - total


def es_sl(c, case):
    pr = case["profit"]
    key = "is_nueva_creacion" if case.get("new_company") else "is_micro"
    v = c.p(key)
    tax = pr * v["value"] if "value" in v else bracket_tax(pr, v["brackets"])
    c.step("Impuesto sobre Sociedades", tax, key.replace("_", " "), v["src"])
    left = pr - tax
    d = 0.0
    if case.get("distribute", True):
        a = c.p("irpf_ahorro")
        d = c.step("IRPF ahorro on dividend", bracket_tax(left, a["brackets"]), "savings scale 19-30%", a["src"])
    c.step("Net to owner", left - d, "")
    c.warn.append("SL: administrator salary, RETA of the socio and SL running costs (gestoría ~€1,200-2,500/yr) not included; estimate.")
    return left - d


# ---------------- United Arab Emirates ----------------

def ae_business(c, case):
    rev, pr = case["revenue"], case["profit"]
    c.step("Revenue", rev, "input")
    c.step("Taxable income", pr, "input")
    sbr = c.p("small_business_relief")
    if case.get("free_zone_qualifying"):
        fz = c.p("free_zone_qualifying")
        tax = c.step("Corporate tax (Qualifying Free Zone)", pr * fz["value"], "0% on qualifying income (conditions and de minimis apply)", fz["src"])
    elif rev <= sbr["revenue_cap"] and case.get("elect_sbr", True):
        tax = c.step("Corporate tax (Small Business Relief)", 0.0, f"revenue <= AED {fmt(sbr['revenue_cap'])}: treated as no taxable income", sbr["src"])
    else:
        ct = c.p("ct")
        tax = c.step("Corporate tax", bracket_tax(pr, ct["brackets"]), "0% up to AED 375,000, 9% above", ct["src"])
    c.step("Personal income tax", 0.0, "UAE has none", c.p("pit")["src"])
    c.step("Net in UAE", pr - tax, "")
    c.step("VAT", f"charge {c.p('vat')['standard']:.0%} if registered", "", c.p("vat")["src"])
    c.warn.append("UAE result is only the UAE side. A Netherlands tax resident (for example) is taxed in NL on worldwide income, and a UAE company managed from NL can be NL tax resident (place of effective management): run the NL case too and ask an advisor.")
    return pr - tax


REGIMES.update({("ES", "autonomo"): es_autonomo, ("ES", "sl"): es_sl, ("AE", "business"): ae_business})


def run(rules, case):
    c = Calc(rules, case["country"], case["year"])
    fn = REGIMES.get((case["country"], case["regime"]))
    if not fn:
        sys.exit(f"Unknown regime {case['country']}/{case['regime']}. Known: {list(REGIMES)}")
    net = fn(c, case)
    cur = rules[case["country"]][str(case["year"])].get("currency") or rules[case["country"]]["2026"]["currency"]
    out = [f"### {case.get('name', case['regime'])} ({case['country']} {case['year']}, {cur})", "",
           "| step | amount | rule | source |", "| --- | ---: | --- | --- |"]
    out += [f"| {l} | {fmt(v)} | {r} | {s} |" for l, v, r, s in c.lines]
    if c.warn:
        out += ["", "Warnings:"] + [f"- {w}" for w in dict.fromkeys(c.warn)]
    return net, "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--rules", default=os.path.join(HERE, "rules.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    rules = json.load(open(a.rules, encoding="utf-8"))
    cases = json.load(open(a.case, encoding="utf-8"))["cases"]
    parts = [f"# Tax calculation (rules reviewed {rules.get('_last_reviewed')})", "",
             "Not tax advice. Each figure shows its rule and source id (see sources.md). Check with an accountant before money moves.", ""]
    summary = []
    for cs in cases:
        net, md = run(rules, cs)
        parts += [md, ""]
        summary.append((cs.get("name", cs["regime"]), net))
    if len(summary) > 1:
        parts += ["## Comparison (net to founder)", "", "| case | net |", "| --- | ---: |"] + [f"| {n} | {fmt(v)} |" for n, v in summary]
    text = "\n".join(parts) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
