const { chromium, firefox, webkit } = require('/opt/playwright/node_modules/playwright');
const { execFileSync } = require('node:child_process');
(async () => {
  const rgba = execFileSync('fc-match', ['-f', '%{rgba}', 'monospace'], { encoding: 'utf8' }).trim();
  if (rgba !== '1') throw new Error(`Expected RGB subpixel rendering (rgba=1), got ${rgba}`);
  const versions = {};
  for (const [name, engine] of Object.entries({ chromium, firefox, webkit })) {
    const browser = await engine.launch({ headless: true });
    try {
      const page = await browser.newPage();
      await page.setContent('<button id="proof">Ready</button><p id="result"></p>');
      await page.evaluate(() => document.querySelector('#proof').onclick = () => document.querySelector('#result').textContent = 'passed');
      await page.click('#proof');
      if (await page.textContent('#result') !== 'passed') throw new Error(`${name} did not execute the page`);
      await page.screenshot({ path: `/workspace/${name}.png` });
      versions[name] = browser.version();
    } finally { await browser.close(); }
  }
  console.log(JSON.stringify({ rgba: Number(rgba), engines: versions }));
})().catch(error => { console.error(error); process.exit(1); });
