# founder-legal: reference

Detail moved out of SKILL.md to save tokens. Read only the part the task needs.

## Step 1: map the law

Write `founder/legal/<project>/<contract>-map.md`: one short table of what applies and
why, each line with a source id and its status:

- **Contract law** chosen (ROME-I art. 3 in the EU; NY-GOL-1401 for New York; Mexican
  parties may choose, with limits) and the rules you cannot contract out of: consumer
  law (UCTD, BW6-AV), general terms (BW6-AV), penalty limits (BW6-94; CCF pena
  convencional, ES-CC art. 1154), moral rights (AW, LFDA, ES-LPI), Spanish payment terms
  (ES-MOROSIDAD), Texas fair notice for indemnities and releases (TX-FAIRNOTICE).
- **Goods across borders**: CISG applies to international B2B sales of goods unless
  excluded. Decide on purpose. Services are outside the CISG.
- **People**: freelancer vs employee (DBA-2025, VBAR-2026, ES-LETA, LFT-2021, CA-AB5),
  placement and agency rules (WAADI, RACT, CA-TAA; Texas has no talent-agency licence
  since 2011, TX-TALENT), platform work (PLATFORM-DIR). Spain: an artist performing for a
  promoter can be an employee for that show (ES-RD1435 until 24 May 2027, then ES-RD607-2026).
- **IP**: who owns what and how it transfers (AW art. 2, ES-LPI, LFDA, USC17).
- **Data**: GDPR art. 28 processor terms (ES-LOPDGDD in Spain), SCC-2021 for transfers,
  LFPDPPP-2025 in Mexico, TX-TDPSA in Texas, CCPA in California.
- **AI**: AI-ACT roles when we build or deploy AI for a client; TX-TRAIGA for Texas.
- **Disputes**: chosen **case by case** (no default home court): use the forum guide in
  clause C-23 (where the counterpart's assets are, amount vs arbitration cost, neutral
  seat) and check the judgment or award can be enforced in the other party's country
  (BRUSSELS-IA, HCCH-2005, NYC-1958).
- **Tax**: VAT, reverse charge, artist withholding: hand the facts to **founder-tax**
  and copy its answer into clause C-21.

A statement that rests on `law-index` or `unverified` gets its status in the text.
Before quoting an article, read it on the official site (`sources.md` URL) using the
research ladder in **founder-cto** (WebSearch, web-fetch, `polite_fetch.py`,
`render_fetch.js`); wetten.overheid.nl refuses robots, so use the web-fetch agent or the
Staatsblad/Kamerstukken PDFs. Update `sources.md` (last checked, status) when you do.

