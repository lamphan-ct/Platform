#!/usr/bin/env python3
"""Build self-contained outputs for the GDS home "Tin đăng đã xem" prototype.

  python3 build.py

prototype.src.html (+ assets/) -> prototype.html  (assets inlined as data URIs)
canvas.template.html + prototype.html -> canvas.html (prototype embedded as srcdoc)
"""
import base64, json, mimetypes, os, re

HERE = os.path.dirname(os.path.abspath(__file__))


def inline_assets(html):
    def sub(m):
        path = os.path.join(HERE, m.group(1))
        mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        with open(path, 'rb') as f:
            return 'data:%s;base64,%s' % (mime, base64.b64encode(f.read()).decode())
    return re.sub(r"(assets/[\w.-]+\.(?:png|jpg))", sub, html)


def main():
    with open(os.path.join(HERE, 'prototype.src.html'), encoding='utf-8') as f:
        proto = inline_assets(f.read())
    with open(os.path.join(HERE, 'prototype.html'), 'w', encoding='utf-8') as f:
        f.write(proto)
    with open(os.path.join(HERE, 'canvas.template.html'), encoding='utf-8') as f:
        canvas = f.read()
    payload = json.dumps(proto, ensure_ascii=False).replace('</', '<\\/')
    canvas = canvas.replace('/*__PROTO__*/', payload)
    with open(os.path.join(HERE, 'canvas.html'), 'w', encoding='utf-8') as f:
        f.write(canvas)
    print('prototype.html %d KB, canvas.html %d KB' % (len(proto) // 1024, len(canvas) // 1024))


if __name__ == '__main__':
    main()
