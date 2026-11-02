// Extrae datos de proyectos y textos para generar páginas estáticas (lo usa build.py)
const fs = require('fs'), path = require('path'), vm = require('vm');
const R = path.dirname(__dirname);
const ctx = { window: { addEventListener() {} }, location: { pathname: '/', search: '' }, history: {}, document: {}, setTimeout() {}, console };
ctx.window.window = ctx.window; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(R, 'dclogic.js'), 'utf8') + '\n' + fs.readFileSync(path.join(R, 'logic.js'), 'utf8'), ctx);
const C = ctx.window.Component; const out = {};
for (const lang of ['es', 'en']) {
  const c = new C({}); c.state.lang = lang; const v = c.renderVals();
  out[lang] = { t: { lead: v.t.lead, work: v.t.work, info: v.t.info, contact: v.t.contact }, projects: v.projects.map(p => ({ title: p.title, slug: p.slug, industry: p.industry, categories: p.categories, year: p.year, info: p.info, cover: p.images[0].src, video: p.images[0].isVideo })) };
}
process.stdout.write(JSON.stringify(out));
