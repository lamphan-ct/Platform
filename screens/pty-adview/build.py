"""Build self-contained index.html (prototype) and canvas.html (prototype + artboard) from the templates."""
import base64, pathlib, re
here = pathlib.Path(__file__).parent
html = (here / 'template.html').read_text(encoding='utf-8')
cache = {}
def uri(name):
    if name not in cache:
        p = here / 'assets' / name
        mime = 'image/jpeg' if p.suffix == '.jpg' else 'image/png'
        cache[name] = f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()
    return cache[name]
NAME = r'[\w-]+\.(?:png|jpg)'
# 1) literal paths (HTML attributes and JS string literals)
html = re.sub(r'assets/(' + NAME + ')', lambda m: uri(m.group(1)), html)
# 2) dynamic paths built in JS templates: assets/${expr} -> ${__A[expr]}
html = re.sub(r'assets/\$\{([^}]+)\}', r'${__A[\1]}', html)
dyn = sorted(set(re.findall(r"'(" + NAME + ")'", html)))
table = 'window.__A={' + ','.join(f'"{n}":"{uri(n)}"' for n in dyn) + '};'
html = html.replace('<script>\n(function () {', '<script>' + table + '</script>\n<script>\n(function () {', 1)
assert 'assets/' not in html, 'unresolved asset path'
(here / 'index.html').write_text(html, encoding='utf-8')
print('index.html', len(html) // 1024, 'KB;', len(dyn), 'dynamic assets')

# canvas.html: prototype + artboard frames, sharing one embedded copy of the page
import json
canvas = (here / 'canvas.template.html').read_text(encoding='utf-8')
payload = json.dumps(html, ensure_ascii=False).replace('</', '<\\/')
canvas = canvas.replace('/*__PROTO__*/', payload, 1)
(here / 'canvas.html').write_text(canvas, encoding='utf-8')
print('canvas.html', len(canvas) // 1024, 'KB')
