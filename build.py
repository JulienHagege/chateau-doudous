#!/usr/bin/env python3
"""Assemble le jeu « Le Château des Doudous ».

- src/part-*.html : morceaux du source (CSS, HTML, JS), concaténés dans l'ordre.
- img/*.png : sprites PixelLab injectés en data URI à la place du marqueur /*IMG*/.
- chateau-doudous.html : source de l'artifact claude.ai (sans doctype, claude.ai ajoute l'enveloppe).
- index.html : version autonome (GitHub Pages, Dropbox) avec doctype, head et reset identiques à l'enveloppe claude.ai.
Usage : python3 build.py
"""
import base64, pathlib, re, json
root = pathlib.Path(__file__).parent
parts = sorted((root/'src').glob('part-*.html'))
src = ''.join(p.read_text(encoding='utf-8') for p in parts)
imgs = {}
for p in sorted((root/'img').glob('*.png')):
    imgs[p.stem] = 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()
src = src.replace('/*IMG*/', json.dumps(imgs))
assert '—' not in src, 'tiret cadratin interdit'
(root/'chateau-doudous.html').write_text(src, encoding='utf-8')
m = re.search(r'<title>.*?</title>\n', src); title = m.group(0)
body = src.replace(title, '', 1).replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '', 1)
out = ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
       + title.strip()
       + '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>'
       + '</head><body>\n' + body + '\n</body></html>\n')
(root/'index.html').write_text(out, encoding='utf-8')
print('chateau-doudous.html :', len(src), 'octets ·  index.html :', len(out), 'octets ·', len(imgs), 'images')
