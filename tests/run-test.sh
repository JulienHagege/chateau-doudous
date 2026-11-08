#!/bin/sh
# Test automatique du Château des Doudous dans Chrome headless (Mac).
# Depuis la racine du projet : sh tests/run-test.sh
# Vérifie : générateurs des 17 salles x 5 niveaux (options, rendu, explications), moteur (une salle complète par salle),
# cycle après Vachou, acquis et célébration, carnet, révision, carte, marche, orage, anti-répétition, refaire après erreur.
set -e
python3 build.py >/dev/null
python3 - <<'PY'
import pathlib
game = pathlib.Path('chateau-doudous.html').read_text()
pathlib.Path('tests/test-built.html').write_text(pathlib.Path('tests/test.html').read_text().replace('<!--GAME-->', game))
PY
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
timeout 150 "$CHROME" --headless=new --disable-gpu --no-sandbox --user-data-dir=/tmp/chateau-chrome-prof --timeout=70000 --dump-dom "file://$PWD/tests/test-built.html" > tests/dump.html 2>/dev/null || true
python3 -c "
import re,html
d=open('tests/dump.html').read(); m=re.search(r'<pre id=\"testout\">([\s\S]*?)</pre>', d); t=html.unescape(m.group(1)) if m else 'pas de sortie'
print('\n'.join(l for l in t.split('\n') if not l.startswith('OK ') and not l.startswith('salle ')))
print('ERREURS' if 'ERREUR' in t or 'ERROR' in t else 'aucune erreur')"
