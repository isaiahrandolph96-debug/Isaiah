// Render UNRESTD PNGs: mockups, print files and a full brand-book image.
//   node clothing-brand/unrestd/tools/render.js
// Google Fonts requests are answered from ../fonts so renders work offline.
const path = require('path');
const fs = require('fs');
let pw;
try { pw = require('playwright'); } catch { pw = require('/opt/node22/lib/node_modules/playwright'); }

const ROOT = path.resolve(__dirname, '..');
const FONTS = path.join(ROOT, 'fonts');
const TILE = '#D6D5CE';

async function localFonts(page) {
  const css = fs.readFileSync(path.join(FONTS, 'fonts.css'), 'utf8')
    .replace(/url\(([^)]+\.woff2)\)/g, 'url(https://fonts.gstatic.com/local/$1)');
  await page.route('https://fonts.googleapis.com/**', r => r.fulfill({ contentType: 'text/css', body: css }));
  await page.route('https://fonts.gstatic.com/**', r => {
    const f = path.join(FONTS, path.basename(new URL(r.request().url()).pathname));
    return fs.existsSync(f) ? r.fulfill({ contentType: 'font/woff2', body: fs.readFileSync(f) }) : r.abort();
  });
}

async function ready(page) {
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.fonts.ready);
}

(async () => {
  const browser = await pw.chromium.launch();

  // 1. one 1200 x 1200 PNG per mockup and per label
  const shot = await browser.newPage({ viewport: { width: 1200, height: 1200 } });
  await localFonts(shot);
  for (const mdir of [path.join(ROOT, 'mockups'), path.join(ROOT, 'labels')])
  for (const f of fs.readdirSync(mdir).filter(f => f.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(mdir, f), 'utf8');
    await shot.setContent(`<body style="margin:0;background:${TILE};display:grid;place-items:center;height:100vh">
      <div style="width:84%;height:84%">${svg.replace('<svg ', '<svg width="100%" height="100%" ')}</div></body>`);
    await ready(shot);
    await shot.screenshot({ path: path.join(mdir, f.replace('.svg', '.png')) });
  }

  // 2. print files, transparent, 4500 x 5400 px
  const pdir = path.join(ROOT, 'print');
  fs.mkdirSync(pdir, { recursive: true });
  const pr = await browser.newPage({ viewport: { width: 1500, height: 1800 }, deviceScaleFactor: 3 });
  await localFonts(pr);
  await pr.goto('file://' + path.join(__dirname, 'print.html'));
  await ready(pr);
  for (const el of await pr.$$('.pf')) {
    const id = (await el.getAttribute('id')).slice(2);
    await el.screenshot({ path: path.join(pdir, `${id}.png`), omitBackground: true });
  }

  // 3. the whole brand book as one image
  const book = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await localFonts(book);
  await book.goto('file://' + path.join(ROOT, 'brand-book.html'));
  await ready(book);
  await book.screenshot({ path: path.join(ROOT, 'brand-book.png'), fullPage: true });
  const hero = await book.$('#drop');
  await hero.screenshot({ path: path.join(ROOT, 'drop-01.png') });

  // 4. the Shift Jacket tech pack, as a two-page PDF for factories
  const tp = await browser.newPage();
  await localFonts(tp);
  await tp.goto('file://' + path.join(__dirname, 'tech-pack.html'));
  await ready(tp);
  await tp.pdf({ path: path.join(ROOT, 'tech-pack-shift-jacket.pdf'), format: 'Letter', printBackground: true,
                 margin: { top: '12mm', bottom: '12mm', left: '12mm', right: '12mm' } });

  await browser.close();
})();
