import { h, render, Fragment } from './vendor/preact.js';

class DCLogic {
  constructor(props) { this.props = props || {}; this.state = {}; }
  setState(patch) { Object.assign(this.state, typeof patch === 'function' ? patch(this.state) : patch); schedule(); }
}
window.DCLogic = DCLogic;

const src = document.getElementById('dc-logic').textContent;
const Component = new Function('DCLogic', src + '\nreturn Component;')(DCLogic);
const comp = new Component({});

const tpl = document.getElementById('tpl').content;
const root = document.getElementById('root');

const ONE = /^\s*\{\{([^{}]+)\}\}\s*$/;
const ANY = /\{\{([\s\S]+?)\}\}/g;

function lookup(expr, scope) {
  expr = expr.trim();
  if (expr === 'true') return true;
  if (expr === 'false') return false;
  if (/^-?\d+(\.\d+)?$/.test(expr)) return Number(expr);
  const parts = expr.split('.');
  let v = scope;
  for (const p of parts) { if (v == null) return undefined; v = v[p]; }
  return v;
}
function val(str, scope) {
  const m = str.match(ONE);
  if (m) return lookup(m[1], scope);
  return str.replace(ANY, (_, e) => { const v = lookup(e, scope); return v == null ? '' : String(v); });
}

const EVENTS = { onclick: 'onClick', onscroll: 'onScroll', onchange: 'onChange', onsubmit: 'onSubmit', oninput: 'onInput' };
const BOOL = { autoplay: 'autoPlay', muted: 'muted', loop: 'loop', playsinline: 'playsInline' };

function toVNodes(node, scope, out) {
  if (node.nodeType === 3) { const t = val(node.nodeValue, scope); if (t !== '') out.push(t); return; }
  if (node.nodeType !== 1) return;
  const tag = node.tagName.toLowerCase();
  if (tag === 'sc-if') {
    if (lookup(node.getAttribute('value').replace(/^\{\{|\}\}$/g, ''), scope)) kids(node, scope, out);
    return;
  }
  if (tag === 'sc-for') {
    const list = lookup(node.getAttribute('list').replace(/^\{\{|\}\}$/g, ''), scope) || [];
    const as = node.getAttribute('as');
    list.forEach((item) => { const s = Object.create(scope); s[as] = item; kids(node, s, out); });
    return;
  }
  const props = {};
  for (const a of node.attributes) {
    const name = a.name;
    if (name.startsWith('hint-')) continue;
    let v = val(a.value, scope);
    if (EVENTS[name]) {
      let ev = EVENTS[name];
      if (ev === 'onChange' && (tag === 'input' || tag === 'textarea')) ev = 'onInput';
      props[ev] = v; continue;
    }
    if (BOOL[name]) { props[BOOL[name]] = v === true || v === 'true'; continue; }
    if (name === 'tabindex') { props.tabIndex = v; continue; }
    props[name] = v;
  }
  const children = [];
  if (tag === 'select' && props['data-options']) {
    children.push(h('option', { value: '' }, props['data-ph']));
    for (const o of props['data-options']) children.push(h('option', { value: o }, o));
    delete props['data-options']; delete props['data-ph'];
  } else kids(node, scope, children);
  out.push(h(tag, props, ...children));
}
function kids(node, scope, out) { for (const c of node.childNodes) toVNodes(c, scope, out); }

let queued = false;
function schedule() { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; draw(); }); }
function draw() {
  const scope = comp.renderVals();
  const out = [];
  kids(tpl, scope, out);
  render(h(Fragment, null, ...out), root);
  document.documentElement.lang = comp.state.lang || 'es';
}
draw();
