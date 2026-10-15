"""Build self-contained mobile.html, desktop.html and canvas.html (both frames side by side) from the templates.

Templates already carry the DS tokens and icon symbols (ds_tokens.py / ds_icons.py inline);
this step only embeds the images under assets/ and logo.png as data URIs.
"""
import base64, json, pathlib, re
here = pathlib.Path(__file__).parent
cache = {}
def uri(path):
    if path not in cache:
        p = here / path
        cache[path] = 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()
    return cache[path]
out = {}
for name in ('mobile', 'desktop'):
    html = (here / f'{name}.template.html').read_text(encoding='utf-8')
    html = re.sub(r'(?<=src=")((?:assets/)?[\w-]+\.png)(?=")', lambda m: uri(m.group(1)), html)
    assert 'assets/' not in html and 'src="logo.png"' not in html, 'unresolved asset path'
    (here / f'{name}.html').write_text(html, encoding='utf-8')
    out[name] = html
    print(f'{name}.html', len(html) // 1024, 'KB')
canvas = (here / 'canvas.template.html').read_text(encoding='utf-8')
enc = lambda s: json.dumps(s, ensure_ascii=False).replace('</', '<\\/')
canvas = canvas.replace('/*__MOBILE__*/', enc(out['mobile']), 1).replace('/*__DESKTOP__*/', enc(out['desktop']), 1)
(here / 'canvas.html').write_text(canvas, encoding='utf-8')
print('canvas.html', len(canvas) // 1024, 'KB')
