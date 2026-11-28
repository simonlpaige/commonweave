// Build the 1200x630 social preview card from tools/share-card.html.
// Needs Playwright with Chromium: node tools/build_share_image.js
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

(async () => {
  const root = path.resolve(__dirname, '..');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(path.join(root, 'tools/share-card.html')).href);
  await page.evaluate(() => document.fonts.ready);
  const target = path.join(root, 'assets/images/commonweave-share.png');
  await page.screenshot({ path: target });
  await browser.close();
  console.log(target);
})();
