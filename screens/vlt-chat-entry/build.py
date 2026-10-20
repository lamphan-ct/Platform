"""Build index.html (standalone prototype, ?t=1|2) and canvas.html (artboards + prototypes for both treatments).

template.html already carries DS tokens and icon symbols; re-inline them after editing with
the screen-builder scripts: ds_tokens.py inline template.html JOB · ds_icons.py inline template.html.
"""
import json, pathlib
here = pathlib.Path(__file__).parent
app = (here / 'template.html').read_text(encoding='utf-8')
(here / 'index.html').write_text(app.replace('<!--BOOT-->', '', 1), encoding='utf-8')
payload = json.dumps(app, ensure_ascii=False).replace('</', '<\\/')
canvas = (here / 'canvas.template.html').read_text(encoding='utf-8').replace('/*__APP__*/', payload, 1)
(here / 'canvas.html').write_text(canvas, encoding='utf-8')
print('index.html', len(app) // 1024, 'KB; canvas.html', len(canvas) // 1024, 'KB')
