"""Build canvas.html: UI cũ (ảnh chụp assets/ui-cu-1512x812.webp) và bản mới (index.html) trên một canvas so sánh.

Chạy: python3 screens/khach-intent/build_canvas.py
Logo PNG được nhúng base64 để canvas.html tự chạy được (artifact một file).
"""
import base64
import json
from pathlib import Path

HERE = Path(__file__).parent
logo = "data:image/png;base64," + base64.b64encode((HERE / "logo.png").read_bytes()).decode()


def embed(name):
    html = (HERE / name).read_text(encoding="utf-8").replace('src="logo.png"', f'src="{logo}"')
    # an toàn khi đặt trong <script type="application/json">
    return json.dumps(html, ensure_ascii=False).replace("</", "<\\/")


tpl = (HERE / "canvas.template.html").read_text(encoding="utf-8")
shot = "data:image/webp;base64," + base64.b64encode((HERE / "assets" / "ui-cu-1512x812.webp").read_bytes()).decode()
out = tpl.replace("/*__OLD__*/", json.dumps(shot)).replace("/*__NEW__*/", embed("index.html"))
(HERE / "canvas.html").write_text(out, encoding="utf-8")
print("wrote", HERE / "canvas.html", len(out), "bytes")
