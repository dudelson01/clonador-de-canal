// Renderiza as artes (legendas + destaques) quadro a quadro com fundo transparente.
// Uso: node ferramentas/arte/render.mjs <spec.json> <saida.mov> [--ini 0] [--fim 32] [--fps 30] [--escala 1]
// Saída: .mov com canal alfa (qtrle), pronto para sobrepor no vídeo com ffmpeg overlay.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf('--' + n); return i >= 0 ? Number(args[i + 1]) : d; };
const [specPath, saida] = args;
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const fps = opt('fps', 30), ini = opt('ini', 0), fim = opt('fim', spec.duracao), esc = opt('escala', 1);
const W = Math.round(1920 * esc), H = Math.round(1080 * esc);

const dir = path.dirname(fileURLToPath(import.meta.url));
// na nuvem usa o Chromium já instalado; no PC do aluno, o do npx playwright install
const exe = '/opt/pw-browsers/chromium';
const browser = await chromium.launch(fs.existsSync(exe) ? { executablePath: exe } : {});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: esc });
await page.goto('file://' + path.join(dir, 'motor.html'));
await page.evaluate(() => document.fonts.ready);
await page.evaluate(s => window.setup(s), spec);
await page.evaluate(async () => { await document.fonts.load('400 50px Anton'); await document.fonts.load('900 50px Mont'); await document.fonts.load('800 50px Mont'); await document.fonts.load('400 50px Bebas'); });

const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
  '-c:v', 'qtrle', '-pix_fmt', 'argb', saida], { stdio: ['pipe', 'inherit', 'inherit'] });

const n = Math.round((fim - ini) * fps);
for (let i = 0; i < n; i++) {
  const t = ini + i / fps;
  await page.evaluate(t => window.render(t), t);
  const png = await page.screenshot({ omitBackground: true, type: 'png' });
  if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 150 === 0) process.stdout.write(`quadro ${i}/${n}\n`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log('ok', saida);
