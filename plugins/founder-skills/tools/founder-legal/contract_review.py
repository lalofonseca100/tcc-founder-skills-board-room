#!/usr/bin/env python3
"""First-pass contract review: clause coverage, red-flag phrases and a risk score.

Standard library only, no network. It reads a contract as plain text (.txt/.md;
convert .docx or .pdf to text first, e.g. `pandoc in.docx -t plain -o in.txt`).

  python3 -I contract_review.py CONTRACT.txt --type services [--assess review.json] [--out report.md]

--type    artist | client | services | nda | supplier | management | partnership | dpa | sale
--assess  optional JSON with a likelihood/impact/balance score per clause (see
          review.example.json). Without it the tool only reports coverage and flags.

Coverage is found by keywords in English, Spanish and Dutch. A keyword hit means
"a clause on this topic seems to exist", never "the clause is good". A person
(and, past the lawyer gates, a lawyer) reads every clause.
"""
import argparse, json, re, sys

FAMILIES = {  # id: (label, [regex keywords, case-insensitive])
    "scope":        ("Scope / deliverables", [r"\bscope\b", r"deliverable", r"\bservices\b", r"\balcance\b", r"\bobjeto\b", r"entregable", r"werkzaamheden", r"\bopdracht\b"]),
    "price":        ("Price and payment terms", [r"\bfees?\b", r"\bprice\b", r"payment", r"invoice", r"honorario", r"\bpago", r"factura", r"\bprijs\b", r"betaling", r"factuur", r"vergoeding", r"commission", r"comisi[oó]n", r"commissie"]),
    "late":         ("Late payment / interest", [r"late payment", r"\binterest\b", r"inter[eé]s(es)? moratorio", r"pena convencional", r"handelsrente", r"wettelijke rente", r"incassokosten"]),
    "acceptance":   ("Acceptance / sign-off", [r"acceptance", r"sign-?off", r"aceptaci[oó]n", r"acceptatie", r"oplevering"]),
    "term":         ("Term and termination", [r"\bterm\b", r"terminat", r"vigencia", r"terminaci[oó]n", r"rescisi[oó]n", r"rescindir", r"looptijd", r"opzegg", r"be[eë]indig", r"ontbind"]),
    "cancel":       ("Cancellation / postponement", [r"cancel", r"postpone", r"cancelaci[oó]n", r"aplazamiento", r"annuler", r"uitstel"]),
    "liability":    ("Limitation of liability", [r"limitation of liability", r"liabilit", r"\bliable\b", r"responsabilidad", r"aansprakelijk"]),
    "indemnity":    ("Indemnity", [r"indemnif", r"hold harmless", r"indemniz", r"sacar en paz y a salvo", r"vrijwar", r"schadeloos"]),
    "insurance":    ("Insurance", [r"insurance", r"\bseguro", r"verzeker"]),
    "ip":           ("Intellectual property / licence", [r"intellectual property", r"copyright", r"licen[cs]e", r"propiedad intelectual", r"derechos? de autor", r"licencia", r"intellectuele eigendom", r"auteursrecht", r"licentie"]),
    "moral":        ("Moral rights / credit", [r"moral rights", r"derechos? morales", r"persoonlijkheidsrecht", r"\bcredit\b", r"cr[eé]dito", r"naamsvermelding"]),
    "confid":       ("Confidentiality", [r"confidential", r"confidencial", r"vertrouwelijk", r"geheimhouding"]),
    "data":         ("Personal data (GDPR / LFPDPPP)", [r"personal data", r"\bgdpr\b", r"datos personales", r"\bavg\b", r"persoonsgegevens", r"aviso de privacidad", r"processor", r"encargado"]),
    "fm":           ("Force majeure", [r"force majeure", r"fuerza mayor", r"caso fortuito", r"overmacht"]),
    "law":          ("Governing law", [r"governing law", r"governed by", r"laws of", r"legislaci[oó]n aplicable", r"leyes (de|aplicables)", r"toepasselijk recht", r"nederlands recht", r"beheerst door"]),
    "disputes":     ("Disputes (court / arbitration / mediation)", [r"arbitrat", r"jurisdiction", r"\bcourts?\b", r"mediat", r"arbitraje", r"tribunales", r"jurisdicci[oó]n", r"mediaci[oó]n", r"geschil", r"bevoegde rechter", r"arbitrage"]),
    "nonsolicit":   ("Non-solicitation / introduction fee", [r"non-?solicit", r"circumvent", r"introduction fee", r"no elusi[oó]n", r"no captaci[oó]n", r"relatiebeding", r"omzeil"]),
    "exclusive":    ("Exclusivity", [r"exclusiv(?!e jurisdiction|e competence)", r"exclusividad", r"exclusiviteit"]),
    "noncompete":   ("Non-compete", [r"non-?compet", r"no competencia", r"concurrentiebeding"]),
    "assign":       ("Assignment / subcontracting", [r"\bassign", r"subcontract", r"cesi[oó]n", r"ceder", r"subcontrat", r"overdra", r"onderaanne"]),
    "status":       ("Independent status (no employment)", [r"independent contractor", r"no employment", r"relaci[oó]n laboral", r"prestador independiente", r"zelfstandig", r"geen arbeidsovereenkomst", r"modelovereenkomst"]),
    "tax":          ("Taxes / VAT / withholding", [r"\bvat\b", r"\bbtw\b", r"\biva\b", r"withholding", r"retenci[oó]n", r"impuesto", r"belasting", r"reverse charge", r"verlegd"]),
    "safety":       ("Safety / permits (events, works)", [r"safety", r"risk assessment", r"permit", r"seguridad", r"permiso", r"protecci[oó]n civil", r"veiligheid", r"vergunning"]),
    "ai":           ("AI and data use", [r"artificial intelligence", r"\bai\b", r"machine learning", r"training data", r"inteligencia artificial", r"kunstmatige intelligentie"]),
    "warranty":     ("Warranties", [r"warrant", r"garant[ií]a", r"garantie", r"represent"]),
    "notices":      ("Notices / changes in writing", [r"notices?\b", r"in writing", r"amend", r"notificaci", r"por escrito", r"modificaci", r"schriftelijk", r"wijziging"]),
    "entire":       ("Entire agreement", [r"entire agreement", r"whole agreement", r"acuerdo (total|[ií]ntegro)", r"totalidad de lo acordado", r"volledige overeenkomst"]),
    "sign":         ("Signatures / e-signature", [r"signature", r"signed", r"firma", r"handtekening", r"ondertekend"]),
    "equity":       ("Equity / vesting / exit", [r"\bequity\b", r"\bshares?\b", r"vesting", r"cliff", r"acciones", r"participaci[oó]n", r"aandelen", r"good leaver|bad leaver", r"drag|tag"]),
    "goods":        ("Delivery / Incoterms / risk of loss", [r"incoterms", r"delivery", r"risk of loss", r"entrega", r"riesgo", r"levering", r"risico"]),
}

REQUIRED = {  # which families a contract of this type should have
    "artist":      ["scope", "price", "cancel", "liability", "insurance", "ip", "moral", "status", "tax", "safety", "fm", "law", "disputes", "term", "data", "sign"],
    "client":      ["scope", "price", "late", "acceptance", "cancel", "liability", "indemnity", "insurance", "ip", "nonsolicit", "safety", "fm", "law", "disputes", "tax", "sign"],
    "services":    ["scope", "price", "late", "acceptance", "term", "liability", "indemnity", "ip", "confid", "data", "ai", "warranty", "law", "disputes", "assign", "status", "sign"],
    "nda":         ["confid", "term", "law", "disputes", "sign"],
    "supplier":    ["scope", "price", "late", "acceptance", "term", "liability", "insurance", "warranty", "confid", "data", "fm", "law", "disputes", "sign"],
    "management":  ["scope", "price", "term", "exclusive", "status", "tax", "confid", "data", "ip", "law", "disputes", "sign"],
    "partnership": ["scope", "equity", "term", "ip", "confid", "noncompete", "nonsolicit", "law", "disputes", "sign"],
    "dpa":         ["data", "confid", "term", "liability", "law", "sign"],
    "sale":        ["scope", "price", "goods", "warranty", "liability", "fm", "law", "disputes", "sign"],
}

RED_FLAGS = [  # (regex, why it matters)
    (r"unlimited liability|responsabilidad ilimitada|onbeperkt aansprakelijk", "Unlimited liability: ask for a cap (e.g. fees paid in the last 12 months)."),
    (r"any and all|cualquier y toda|alle en elke", "'Any and all' wording: very wide; narrow it to direct, foreseeable losses."),
    (r"sole (and absolute )?discretion|a su (entera|sola) discreci[oó]n|naar eigen (goed)?dunken|naar eigen inzicht", "One party decides alone: add objective criteria or 'acting reasonably'."),
    (r"perpetu|perpetuidad|eeuwigdurend|voor onbepaalde tijd", "Perpetual right or duty: add an end date or a way out."),
    (r"irrevocabl|irrevocable|onherroepelijk", "Irrevocable: check you can still terminate for breach."),
    (r"automatic(ally)? renew|renovaci[oó]n autom[aá]tica|stilzwijgend verlengd|automatisch verlengd", "Automatic renewal: diarise the notice date; in NL B2C max 1 month notice after renewal."),
    (r"\bexclusiv(?!e jurisdiction|e competence)|exclusividad|exclusiviteit", "Exclusivity: is it limited by territory, time and a minimum performance?"),
    (r"non-?compet|no competencia|concurrentiebeding", "Non-compete: often unenforceable or limited (US state law, NL art. 7:653 BW for employees, MX art. 5 Constitución); keep it narrow."),
    (r"waive[sd]? (all|any)? ?moral rights|renuncia a (los )?derechos morales|afstand van (persoonlijkheids)?rechten", "Moral-rights waiver: not possible under MX law; limited in NL (art. 25 Auteurswet)."),
    (r"work (made )?for hire|obra por encargo", "Work-for-hire: under US law only for listed work types with a signed writing (17 U.S.C. 101); elsewhere use an assignment."),
    (r"all rights|todos los derechos|alle rechten", "'All rights' transfer: list the rights, media, territory, time and fee per use."),
    (r"liquidated damages|penalt|pena convencional|penalizaci[oó]n|\bboete", "Penalty / liquidated damages: check it is proportionate (NL art. 6:94 BW; MX art. 1843 CCF caps at the main obligation)."),
    (r"personal(ly)? guarantee|aval|obligado solidario|fiador|hoofdelijk|borg", "Personal guarantee: you would pay from private assets. Lawyer gate."),
    (r"time is of the essence", "'Time is of the essence' (US/UK): any delay may allow termination."),
    (r"without (prior )?notice|sin (previo )?aviso|zonder (voorafgaande )?(kennisgeving|opzegging)", "Action without notice: ask for written notice and a cure period."),
    (r"unilateral|eenzijdig", "Unilateral change right: changes should need both signatures."),
    (r"indemnif[a-z]* .{0,60}(any|all) (claims?|losses)", "Broad indemnity: limit to third-party claims caused by the indemnifier's breach."),
    (r"(own|sole) negligence|regardless of (its|their|any) (own )?negligence|propia negligencia", "Covers a party's own negligence: in Texas it must be express and conspicuous (fair notice); refuse it if it is against us."),
    (r"worldwide|todo el mundo|wereldwijd", "Worldwide scope: is it needed? Price it or narrow it."),
    (r"jury trial|juicio por jurado", "US jury-trial clause: check the forum; consider arbitration."),
    (r"exclusive jurisdiction of the courts of (?!the netherlands|amsterdam|rotterdam)", "Foreign exclusive court: suing there is costly. Prefer your home court or arbitration."),
]


def load(path):
    try:
        return open(path, encoding="utf-8").read()
    except UnicodeDecodeError:
        return open(path, encoding="latin-1").read()


def scan(text, ctype):
    lines = text.splitlines()
    low = [l.lower() for l in lines]
    found = {}
    for fid, (_, pats) in FAMILIES.items():
        hits = [i + 1 for i, l in enumerate(low) if any(re.search(p, l) for p in pats)]
        if hits:
            found[fid] = hits
    flags = []
    for pat, why in RED_FLAGS:
        for i, l in enumerate(low):
            if re.search(pat, l):
                flags.append((i + 1, lines[i].strip()[:110], why))
    flags.sort()
    req = REQUIRED[ctype]
    missing = [f for f in req if f not in found]
    return found, flags, req, missing


def score(assess):
    """Each clause: likelihood 1-5, impact 1-5, balance -2..+2 (negative = against us)."""
    rows, reds, ambers = [], 0, 0
    for c in assess.get("clauses", []):
        L, I, B = int(c["likelihood"]), int(c["impact"]), int(c.get("balance", 0))
        risk = L * I
        if B <= -2 or B >= 2:  # one-sided either way is a risk (unenforceable, or the relationship breaks)
            risk = min(25, risk + 3)
        band = "RED" if risk >= 15 else "AMBER" if risk >= 8 else "GREEN"
        reds += band == "RED"; ambers += band == "AMBER"
        rows.append((c["clause"], L, I, B, risk, band, c.get("fix", ""), c.get("source", "")))
    worst = max((r[4] for r in rows), default=0)
    avg = sum(r[4] for r in rows) / len(rows) if rows else 0
    # 100 = no risk; the worst clause weighs as much as the average of all
    health = round(100 - (0.5 * worst + 0.5 * avg) * 4)
    grade = "Do not sign as is" if reds else "Sign after fixes" if ambers else "OK to sign"
    return rows, max(0, health), grade


LAWYER_GATES = [
    "any RED clause after negotiation",
    "contract value above EUR 25,000 / MXN 500,000 / USD 25,000, or term over 3 years (thresholds approved by the founder 2026-11-02)",
    "equity, shareholder, vesting or company formation (B.V., Stichting, S.A.P.I., LLC)",
    "employment, placement of workers, agency licensing (NL Waadi, MX LFT/REPSE, ES artist regime RD 1435/1985 -> RD 607/2026, California Talent Agencies Act)",
    "transfer of core IP, exclusivity, or a non-compete",
    "personal guarantee, security over assets, or loans",
    "special-category personal data, minors, or transfers of personal data outside the EU/EEA",
    "a dispute, claim, debt collection or termination for breach already under way",
    "a foreign governing law or court that we have not used before",
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("contract")
    ap.add_argument("--type", required=True, choices=sorted(REQUIRED))
    ap.add_argument("--assess")
    ap.add_argument("--out")
    a = ap.parse_args()
    text = load(a.contract)
    found, flags, req, missing = scan(text, a.type)
    out = [f"# Contract review (first pass): {a.contract}", "",
           f"Type: **{a.type}**. Words: {len(text.split())}. Keyword scan only: every clause still needs reading.", "",
           "## 1. Coverage of the checklist", "", "| clause | status | lines |", "| --- | --- | --- |"]
    for f in req:
        out.append(f"| {FAMILIES[f][0]} | {'found' if f in found else '**MISSING**'} | {', '.join(map(str, found.get(f, [])[:8]))} |")
    extra = [f for f in found if f not in req]
    if extra:
        out += ["", "Also present (not required for this type): " + ", ".join(FAMILIES[f][0] for f in extra) + "."]
    out += ["", f"Missing: {len(missing)} of {len(req)}.", "", "## 2. Red-flag wording", ""]
    if flags:
        out += ["| line | text | why it matters |", "| --- | --- | --- |"]
        out += [f"| {n} | {t.replace('|', '/')} | {w} |" for n, t, w in flags]
    else:
        out.append("No red-flag wording found by the scan.")
    if a.assess:
        rows, health, grade = score(json.load(open(a.assess)))
        out += ["", "## 3. Risk score (likelihood x impact, balance adjusts)", "",
                "| clause | L | I | balance | risk | band | proposed fix | source |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        out += [f"| {c} | {L} | {I} | {B:+d} | {r} | {b} | {fx} | {s} |" for c, L, I, B, r, b, fx, s in rows]
        out += ["", f"**Contract health: {health}/100. Verdict: {grade}.**"]
    out += ["", "## 4. Lawyer gates (if any applies, a licensed lawyer reviews before signing)", ""]
    out += [f"- [ ] {g}" for g in LAWYER_GATES]
    out += ["", "_Not legal advice. A first pass to prepare a review or a lawyer brief._"]
    report = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(report)
        print(f"wrote {a.out}")
    else:
        sys.stdout.write(report)


if __name__ == "__main__":
    main()
