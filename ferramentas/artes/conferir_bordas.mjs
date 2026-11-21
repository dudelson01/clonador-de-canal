// Confere se alguma arte sai da tela: desenha cada arte no estado cheio (antes de sumir) e mede tudo que foi desenhado.
// Uso: node conferir_bordas.mjs artes.json [pasta_png_opcional]
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'fs'; import path from 'path'; import url from 'url';
const [,, arq, pasta] = process.argv;
const artes = JSON.parse(fs.readFileSync(arq, 'utf8'));
const pagina = url.pathToFileURL(path.join(path.dirname(url.fileURLToPath(import.meta.url)), 'artes.html')).href;
const exe = '/opt/pw-browsers/chromium';
const browser = await chromium.launch(fs.existsSync(exe) ? { executablePath: exe } : {});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(pagina);
await page.evaluate(() => document.fonts.ready);
let ruins = 0;
for (const a of artes) {
  const t = Math.max(0.05, a.dur - 0.25);
  const r = await page.evaluate(([a, t]) => { window.quadro(a, t, a.dur);
    let L = 1e9, R = -1e9, T = 1e9, B = -1e9;
    for (const el of document.querySelectorAll('#palco *')) { const b = el.getBoundingClientRect(); if (!b.width || !b.height) continue;
      if (el.tagName === 'svg' || el.closest('svg')) continue;
      L = Math.min(L, b.left); R = Math.max(R, b.right); T = Math.min(T, b.top); B = Math.max(B, b.bottom); }
    return { L, R, T, B }; }, [a, t]);
  const fora = r.L < 20 || r.R > 1900 || r.T < 10 || r.B > 1070;
  if (fora) ruins++;
  console.log(`${fora ? 'FORA' : 'ok  '} ${a.id} ${a.tipo} [${Math.round(r.L)}..${Math.round(r.R)} x ${Math.round(r.T)}..${Math.round(r.B)}] ${(a.texto || a.titulo || '').slice(0, 40)}`);
  if (pasta && fora) await page.screenshot({ path: path.join(pasta, a.id + '.png'), omitBackground: true });
}
console.log('artes fora da tela:', ruins);
await browser.close();
