#!/usr/bin/env python3
"""Genera index.html, logic.js y las páginas de cada sección y proyecto a partir de src/page.html
(sin eval, compatible con CSP estricta). Correr siempre después de editar src/page.html."""
import os, re, json, html as H, subprocess, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://noeliaorona.com'
s = open(os.path.join(R, 'src/page.html')).read()
a = s.index('<script type="text/plain" id="dc-logic">'); b = s.index('</script>', a)
logic = s[s.index('>', a) + 1:b]
open(os.path.join(R, 'logic.js'), 'w').write('/* generado por tools/build.py */\n' + logic.strip() + '\nwindow.Component = Component;\n')
base = s[:a] + '<script src="dclogic.js"></script>\n<script src="logic.js"></script>' + s[b + len('</script>'):]
open(os.path.join(R, 'index.html'), 'w').write(base)

data = json.loads(subprocess.check_output(['node', os.path.join(R, 'tools/extract.js')]))
clean = lambda t: re.sub(r'\s+', ' ', (t or '').replace(' ', ' ')).strip()
def cut(t, n=158):
    t = clean(t)
    if len(t) <= n: return t
    t = t[:n].rsplit(' ', 1)[0].rstrip(',;:—-')
    return t + '…'

def page(html, title, desc, url, image=None, extra_ld=None):
    e = lambda v: H.escape(v, quote=True)
    html = re.sub(r'<title>.*?</title>', '<title>' + e(title) + '</title>', html, count=1)
    html = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + e(desc) + '">', html, count=1)
    html = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="' + e(title) + '">', html, count=1)
    html = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="' + e(desc) + '">', html, count=1)
    html = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="' + url + '">', html, count=1)
    html = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="' + url + '">', html, count=1)
    if image:
        html = re.sub(r'<meta property="og:image" content="[^"]*">', '<meta property="og:image" content="' + image + '">', html, count=1)
        html = re.sub(r'<meta name="twitter:image" content="[^"]*">', '<meta name="twitter:image" content="' + image + '">', html, count=1)
        html = re.sub(r'<meta property="og:image:width" content="\d+">', '<meta property="og:image:width" content="1200">', html, count=1)
        html = re.sub(r'<meta property="og:image:height" content="\d+">', '<meta property="og:image:height" content="630">', html, count=1)
        html = re.sub(r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="' + e(title) + '">', html, count=1)
    if extra_ld:
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        ld = json.loads(m.group(1)); ld['@graph'] += extra_ld
        html = html[:m.start(1)] + json.dumps(ld, ensure_ascii=False, separators=(',', ':')) + html[m.end(1):]
    return html

def crumbs(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}

HOME = (SITE + '/')
sections = {
    'sobre-mi': ('Sobre mí — Noelia Orona', 'Noelia Orona, diseñadora con base en Buenos Aires y más de 5 años de experiencia en identidad visual, rebranding, diseño editorial, packaging y web.', 'Sobre mí'),
    'proyectos': ('Proyectos — Noelia Orona', 'Identidad visual, rebranding, editorial y packaging para real estate, hotelería, cultura y lifestyle: ' + ', '.join(p['title'] for p in data['es']['projects'][:4]) + ' y más.', 'Proyectos'),
    'contacto': ('Contacto — Noelia Orona', 'Contame tu proyecto. Identidad visual, rebranding, diseño editorial y web desde Buenos Aires, Argentina.', 'Contacto'),
    'privacidad': ('Privacidad — Noelia Orona', 'Cómo se tratan los datos en noeliaorona.com: sin cookies, sin seguimiento y con tus derechos según la Ley 25.326.', 'Privacidad'),
}
urls = [HOME]
for slug, (title, desc, name) in sections.items():
    url = SITE + '/' + slug
    ld = [crumbs([('Noelia Orona', HOME), (name, url)])]
    if slug == 'proyectos':
        ld.append({'@type': 'CollectionPage', '@id': url + '#page', 'url': url, 'name': title, 'isPartOf': {'@id': SITE + '/#web'},
                   'hasPart': [{'@id': SITE + '/proyectos/' + p['slug'] + '#work'} for p in data['es']['projects']]})
    open(os.path.join(R, slug + '.html'), 'w').write(page(base, title, desc, url, extra_ld=ld))
    urls.append(url)

os.makedirs(os.path.join(R, 'proyectos'), exist_ok=True)
os.makedirs(os.path.join(R, 'og'), exist_ok=True)
from PIL import Image
for p, pe in zip(data['es']['projects'], data['en']['projects']):
    url = SITE + '/proyectos/' + p['slug']
    og = os.path.join(R, 'og', p['slug'] + '.jpg')
    src = os.path.join(R, p['cover'])
    if not p['video'] and (not os.path.exists(og) or os.path.getmtime(og) < max(os.path.getmtime(src), os.path.getmtime(__file__))):
        im = Image.open(src)
        if getattr(im, 'n_frames', 1) > 1:  # animada: usar el cuadro con más contenido
            from PIL import ImageStat
            best = max(range(0, im.n_frames, 4), key=lambda k: (im.seek(k), sum(ImageStat.Stat(im.convert('L')).stddev))[1]); im.seek(best)
        im = im.convert('RGBA'); bgc = Image.new('RGBA', im.size, (239, 239, 239, 255)); bgc.alpha_composite(im); im = bgc.convert('RGB')
        im.thumbnail((1200, 630), Image.LANCZOS)
        # fondo: color medio del borde de la imagen, para que la portada entre completa sin recortes
        px = list(im.crop((0, 0, im.width, 2)).get_flattened_data()) + list(im.crop((0, im.height - 2, im.width, im.height)).get_flattened_data()) + list(im.crop((0, 0, 2, im.height)).get_flattened_data()) + list(im.crop((im.width - 2, 0, im.width, im.height)).get_flattened_data())
        col = tuple(sorted(c[k] for c in px)[len(px) // 2] for k in range(3))
        canvas = Image.new('RGB', (1200, 630), col); canvas.paste(im, ((1200 - im.width) // 2, (630 - im.height) // 2))
        canvas.save(og, quality=86, optimize=True, progressive=True)
    info = p['info']
    title = p['title'] + ' — ' + clean(p['categories']).split(',')[0] + ' | Noelia Orona'
    desc = cut(info['client'] + '. ' + info['challenge'])
    work = {'@type': 'CreativeWork', '@id': url + '#work', 'url': url, 'name': p['title'], 'headline': p['title'],
            'description': clean(info['challenge'] + ' ' + info['solution']), 'abstract': clean(info['client']),
            'genre': clean(p['industry']), 'keywords': clean(p['categories']), 'inLanguage': 'es',
            'image': SITE + '/og/' + p['slug'] + '.jpg', 'creator': {'@id': SITE + '/#noelia'}, 'author': {'@id': SITE + '/#noelia'},
            'isPartOf': {'@id': SITE + '/proyectos#page'},
            'workTranslation': {'@type': 'CreativeWork', 'inLanguage': 'en', 'name': pe['title'], 'description': clean(pe['info']['challenge'] + ' ' + pe['info']['solution'])}}
    if p['year']: work['dateCreated'] = p['year']
    ld = [work, crumbs([('Noelia Orona', HOME), ('Proyectos', SITE + '/proyectos'), (p['title'], url)])]
    open(os.path.join(R, 'proyectos', p['slug'] + '.html'), 'w').write(page(base, title, desc, url, SITE + '/og/' + p['slug'] + '.jpg', ld))
    urls.append(url)

# 404: muestra la home, sin indexar
nf = page(base, 'Página no encontrada — Noelia Orona', 'Esta página no existe. Volvé al inicio de noeliaorona.com.', HOME)
nf = nf.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
open(os.path.join(R, '404.html'), 'w').write(nf)

today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm += ['  <url><loc>%s</loc><lastmod>%s</lastmod></url>' % (u, today) for u in urls]
sm += ['</urlset>', '']
open(os.path.join(R, 'sitemap.xml'), 'w').write('\n'.join(sm))
print('ok', len(urls), 'páginas')
