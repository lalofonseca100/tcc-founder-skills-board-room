#!/usr/bin/env node
// render_fetch.js - read JavaScript-heavy pages in a real headless browser (founder-cto).
// Same rules as polite_fetch.py: robots.txt first, slow, named, dated copies + ledger.csv.
// Usage: node render_fetch.js --out founder/cto/sources [--delay 3] URL [URL ...]
// Never use it to log in, solve CAPTCHAs, bypass paywalls or collect personal data.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), crypto = require('crypto');

const args = process.argv.slice(2); let out = 'founder/cto/sources', delay = 3; const urls = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--out') out = args[++i];
  else if (args[i] === '--delay') delay = Number(args[++i]);
  else urls.push(args[i]);
}
if (!urls.length) { console.error('give at least one URL'); process.exit(1); }
const UA = 'FounderSkills-Research-Bot/1.0 (+founder research; contact via site owner)';
const polite = path.join(__dirname, 'polite_fetch.py');
const robots = (u) => { try { execFileSync('python3', ['-I', polite, '--robots-only', u], { stdio: 'pipe' }); return 'allowed'; }
  catch (e) { return e.status === 2 ? 'disallowed' : 'unreadable'; } };
const csvq = (v) => '"' + String(v).replace(/"/g, '""') + '"';

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const ledger = path.join(out, 'ledger.csv');
  if (!fs.existsSync(ledger)) fs.writeFileSync(ledger, 'fetched_utc,status,url,title,file,sha256,links_found\n');
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const browser = await chromium.launch({ proxy });
  const ctx = await browser.newContext({ userAgent: UA });
  for (const url of urls) {
    const now = new Date().toISOString().slice(0, 16) + 'Z';
    const r = robots(url);
    if (r !== 'allowed') { fs.appendFileSync(ledger, [now, 'skipped-robots-' + r, url, '', '', '', 0].map(csvq).join(',') + '\n'); console.log('SKIP', r, url); continue; }
    const page = await ctx.newPage();
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
      for (let i = 0; i < 5; i++) { await page.mouse.wheel(0, 4000); await page.waitForTimeout(500); } // load lazy content
      const title = await page.title();
      const text = await page.evaluate(() => document.body.innerText);
      const links = await page.evaluate(() => [...document.querySelectorAll('a[href]')].map(a => a.href));
      const sha = crypto.createHash('sha256').update(text).digest('hex'); const file = 'r-' + sha.slice(0, 12) + '.txt';
      fs.writeFileSync(path.join(out, file), `URL: ${url}\nTITLE: ${title}\nFETCHED: ${now} (rendered)\n\n${text}\n\nLINKS:\n${links.join('\n')}\n`);
      fs.appendFileSync(ledger, [now, 'ok-rendered', url, title, file, sha, links.length].map(csvq).join(',') + '\n'); console.log('OK', url, '->', file);
    } catch (e) { fs.appendFileSync(ledger, [now, 'error:' + e.name, url, '', '', '', 0].map(csvq).join(',') + '\n'); console.log('ERR', url, e.message.split('\n')[0]); }
    await page.close(); await new Promise(res => setTimeout(res, delay * 1000));
  }
  await browser.close();
})();
