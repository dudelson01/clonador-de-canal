// Renderiza artes (ferramentas/artes/artes.html) quadro a quadro em PNG transparente.
// Uso: node render_artes.mjs artes.json pasta_saida [fps=30]
// artes.json = [{"id":"a1","dur":1.2, ...campos da arte}]  -> pasta_saida/<id>/%04d.png
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'fs'; import path from 'path'; import url from 'url';
const [,, arq, saida, fpsArg] = process.argv;
const fps = Number(fpsArg || 30);
const artes = JSON.parse(fs.readFileSync(arq, 'utf8'));
const pagina = url.pathToFileURL(path.join(path.dirname(url.fileURLToPath(import.meta.url)), 'artes.html')).href;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(pagina);
await page.evaluate(() => document.fonts.ready);
for (const a of artes) {
  const dir = path.join(saida, a.id); fs.mkdirSync(dir, { recursive: true });
  const n = Math.round(a.dur * fps);
  for (let i = 0; i < n; i++) {
    await page.evaluate(([a, t, d]) => window.quadro(a, t, d), [a, i / fps, a.dur]);
    await page.screenshot({ path: path.join(dir, String(i).padStart(4, '0') + '.png'), omitBackground: true });
  }
  console.log('ok', a.id, n, 'quadros');
}
await browser.close();
