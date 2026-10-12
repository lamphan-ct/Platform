#!/usr/bin/env python3
"""Build the Save → Compare drawer prototype (Nhà Tốt / PTY).

Built per design-chotot/screen-builder-and-prototype v2.1.0:
  product Nhà Tốt · mobile iPhone frame · combined flow + interaction ·
  spec-ready (data-ds-*) · partial scope (host adview-pty is reference only).

Outputs
  index.html                     self-contained HTML (inline CSS/JS, DS sprite symbols, base64 images)
  --canvas <dir>                 also writes <dir>/SkillFlow.dc.html + SkillProto.dc.html for the Design canvas

Icons come only from the DS sprite (ds-symbols.txt = verbatim <symbol> lines from
references/icons/sprite.svg). Colours only through semantic tokens declared in :root.
"""
import base64, io, json, os, sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, '..', 'pty-adview', 'assets')

# ---------------------------------------------------------------- data
POOL = [
    dict(id=0, src='just', img='hero.jpg', title='Bán gấp căn nhà ở ngay chợ Bờ Ngựa, hưng nhơn, 5mx19,2m, giá 1 tỷ1',
         price='3,25 tỷ', area='50 m²', ppm=45.69, loc='Quận 12 (P. Thạnh Xuân)', sub='Quận 12 (P. Thạnh Xuân)',
         legal='Sổ hồng', type='Nhà mặt phố', bed='3 PN', wc='2 WC', furn='Nội thất cơ bản', floors='2 tầng', dir='Đông Nam'),
    dict(id=1, src='saved', img='sp3.jpg', title='Nhà 1 trệt 2 lầu hẻm 5m, Thạnh Xuân 13, sổ hồng riêng',
         price='3,4 tỷ', area='52 m²', ppm=65.38, loc='Quận 12', sub='Đã lưu · 3 ngày trước',
         legal='Sổ hồng', type='Nhà ngõ, hẻm', bed='3 PN', wc='3 WC', furn='Full nội thất', floors='3 tầng', dir='Đông Nam'),
    dict(id=2, src='saved', img='sp4.jpg', title='Nhà mặt tiền đường Lê Thị Riêng, gần chợ Thới An',
         price='3,6 tỷ', area='56 m²', ppm=64.29, loc='Quận 12', sub='Đã lưu · 1 tuần trước',
         legal='Sổ hồng', type='Nhà mặt phố', bed='3 PN', wc='', furn='Nội thất cơ bản', floors='2 tầng', dir=''),
    dict(id=3, src='viewed', img='sp1.jpg', title='Nhà hẻm xe hơi Thạnh Xuân 25, 1 trệt 1 lầu, sổ riêng',
         price='2,95 tỷ', area='45 m²', ppm=65.56, loc='Quận 12', sub='Đã xem · 2 giờ trước',
         legal='Sổ hồng', type='Nhà ngõ, hẻm', bed='2 PN', wc='2 WC', furn='', floors='2 tầng', dir='Tây Bắc'),
    dict(id=4, src='viewed', img='sp2.jpg', title='Nhà mới xây 4x12m, hẻm thông Lê Quang Hòa',
         price='3,1 tỷ', area='48 m²', ppm=64.58, loc='Quận 12', sub='Đã xem · Hôm qua',
         legal='Sổ chung', type='Nhà ngõ, hẻm', bed='3 PN', wc='2 WC', furn='Full nội thất', floors='3 tầng', dir='Đông'),
    dict(id=5, src='other', img='ad1.jpg', title='Nhà phố 1 trệt 2 lầu, Thạnh Lộc, gần trường học',
         price='3,3 tỷ', area='50 m²', ppm=66.0, loc='Quận 12', sub='Tin trên Nhà Tốt',
         legal='Sổ hồng', type='Nhà mặt phố', bed='3 PN', wc='3 WC', furn='', floors='3 tầng', dir='Nam'),
    dict(id=6, src='other', img='ad3.jpg', title='Nhà hẻm 6m An Phú Đông, 5x10m, đã hoàn công',
         price='3,5 tỷ', area='50 m²', ppm=70.0, loc='Quận 12', sub='Tin trên Nhà Tốt',
         legal='Sổ hồng', type='Nhà ngõ, hẻm', bed='4 PN', wc='3 WC', furn='Nội thất cơ bản', floors='3 tầng', dir=''),
]
SECTIONS = [('saved', 'Chọn thêm tin đã lưu'), ('viewed', 'Chọn thêm tin đã xem - chưa lưu'), ('other', 'Tin khác trên Nhà Tốt')]
SRC_ICON = {'saved': 'Heart-fill', 'viewed': 'Heart-outline'}
CMP_SECTIONS = [
    ('Giá & Diện tích', ['price', 'ppm', 'area']),
    ('Pháp lý, loại hình', ['legal', 'type']),
    ('Số phòng ngủ, vệ sinh', ['bed', 'wc']),
    ('Nội thất, số tầng, hướng', ['furn', 'floors', 'dir']),
]
MAX = 4


def fmt_ppm(n):
    s = ('%.2f' % n).rstrip('0').rstrip('.')
    return s.replace('.', ',') + ' tr/m²'


# ---------------------------------------------------------------- image + attr helpers
class Ctx:
    """Rendering context. inline=True → base64 images (self-contained repo file); else canvas asset paths."""
    def __init__(self, inline):
        self.inline = inline
        self._cache = {}
        self.rules = {}

    def tag(self, name, w, cls, attrs=''):
        """<img> on the canvas; in the self-contained file each image is one shared CSS background (no duplicated base64)."""
        if not self.inline:
            return '<img class="%s" src="assets/%s" alt="" %s>' % (cls, name, attrs)
        key = 'im-%s-%d' % (name.split('.')[0], w)
        self.img(name, w)
        self.rules[key] = self._cache[(name, w)]
        return '<span class="%s %s" role="img" aria-label="" %s></span>' % (cls, key, attrs)

    def css(self):
        return ''.join('.%s{background:center/cover no-repeat url(%s)}' % (k, v) for k, v in self.rules.items())

    def img(self, name, w):
        if not self.inline:
            return 'assets/' + name
        key = (name, w)
        if key not in self._cache:
            from PIL import Image
            im = Image.open(os.path.join(ASSETS, name)).convert('RGB')
            h = round(im.height * w / im.width)
            im = im.resize((w, h), Image.LANCZOS)
            buf = io.BytesIO(); im.save(buf, 'JPEG', quality=78, optimize=True)
            self._cache[key] = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
        return self._cache[key]


def ds(**kw):
    """data-ds-* attributes. ds(ds='Button', type='Primary') → data-ds="Button" data-ds-type="Primary"."""
    out = []
    for k, v in kw.items():
        if v is None:
            continue
        name = 'data-ds' if k == 'ds' else 'data-ds-' + k.replace('_', '-')
        out.append('%s="%s"' % (name, escape(str(v))))
    return ' '.join(out)


def icon(i, size=24, cls='', extra=''):
    sz = '' if size == 24 else ' ds-icon--%d' % size
    return '<svg class="ds-icon%s %s" aria-hidden="true" %s><use href="#ds-%s"/></svg>' % (sz, cls, extra, i)


def T(tag, typo, color, text, cls='', extra=''):
    """Text node with mandatory typo + colour annotation."""
    return '<%s class="ty-%s c-%s %s" %s %s>%s</%s>' % (tag, typo, color, cls, ds(typo=typo, color=color), extra, text, tag)


REF = 'data-ds-context="reference"'

# ---------------------------------------------------------------- host (reference only)
def host_adview(c, saved=False, save_attr=''):
    """Minimal AdView PTY context: rendered only to show where the drawer is triggered. Not handed off."""
    heart = 'Heart-fill' if saved else 'Heart-outline'
    label = 'Đã lưu' if saved else 'Lưu'
    return f'''
<div class="host" {REF}>
  <div class="host-hero">{c.tag('hero.jpg', 375, 'host-im')}
    <div class="host-nav">
      <span class="host-ib">{icon('Arrowleft-outline')}</span>
      <span class="host-sp"></span>
      <span class="host-ib">{icon('Share-outline')}</span>
      <span class="host-ib">{icon('Ellipsis-outline')}</span>
    </div>
  </div>
  <div class="host-body">
    <p class="ty-header-section c-text-primary">Bán gấp căn nhà ở ngay chợ Bờ Ngựa, hưng nhơn, 5mx19,2m, giá 1 tỷ1</p>
    <p class="host-price"><b class="ty-display-annotation c-text-brand">3,25 tỷ</b><span class="ty-body-section c-text-secondary">· 50 m² · 45,69 tr/m²</span></p>
    <p class="host-loc ty-body-caption c-text-secondary">{icon('Location-outline', 16)}Quận 12 (P. Thạnh Xuân)</p>
    <div class="host-ph"></div><div class="host-ph s"></div><div class="host-ph"></div><div class="host-ph m"></div>
  </div>
  <div class="host-bar">
    <button class="host-save {'on' if saved else ''}" {save_attr} aria-pressed="{str(saved).lower()}" {ds(ds='Button', type='Tertiary', size='L-40', state='Active', pill='false', icon=heart, context='reference', on_tap='save → open drawer (unsaved) | unsave → snackbar')}>{icon(heart, 20, 'save-ic')}<span class="ty-label-section">{label}</span></button>
    <button class="host-btn sec">{icon('Chat-outline', 20)}<span class="ty-label-section">Chat</span></button>
    <button class="host-btn pri">{icon('Phone-outline', 20)}<span class="ty-label-section">Gọi</span></button>
  </div>
</div>'''


# ---------------------------------------------------------------- drawer (new — handoff scope)
def pick_item(c, p, on, delay, dyn=None):
    """One selectable ad row. dyn=(clsHole, tapHole) for the canvas prototype."""
    cls = dyn[0] if dyn else ('on' if on else '')
    tap = ('onClick="%s"' % dyn[1]) if dyn else ('data-id="%d"' % p['id'])
    just = p['src'] == 'just'
    sub_icon = 'Location-outline' if just else SRC_ICON.get(p['src'])
    sub_ic_color = 'icon-secondary' if just else ('icon-brand' if p['src'] == 'saved' else 'icon-secondary')
    sub = (icon(sub_icon, 16, 'c-' + sub_ic_color, ds(icon=sub_icon, color=sub_ic_color)) if sub_icon else '') + escape(p['sub'])
    return f'''
<div class="pk-item {cls}" role="checkbox" tabindex="0" {tap} style="--d:{delay}ms" {ds(ds='List item / selectable', state='Default', gap='gap-small-12', pad='padding-small-12 padding-medium-16', on_tap='toggle select (max 4 → snackbar)', raw='enter stagger k×25ms intentional')}>
  <span class="cb" {ds(ds='Checkbox', type='Standard', size='24', state='Default', pill='false', icon='Check-outline', raw='motion pop 220ms / bump / enter-stagger kept from prototype intentional')}><span class="cb-box">{icon('Check-outline', 16)}</span></span>
  {c.tag(p['img'], 128, 'pk-th', ds(radius='radius-card-small', size='64x64'))}
  <span class="pk-tx">
    {T('span', 'body-section', 'text-primary', escape(p['title']), 'pk-ttl', ds(content_rule='max-2-lines, ellipsis'))}
    <span class="pk-pr">{T('b', 'label-section', 'text-primary', p['area'] + ' - ' + p['price'])}{T('span', 'body-caption', 'text-secondary', fmt_ppm(p['ppm']))}</span>
    {T('span', 'body-caption', 'text-tertiary', sub, 'pk-sub')}
  </span>
</div>'''


def drawer(c, sel=(0,), history=True, cta_bump='', dyn=False, closing=False, show_saved_item=True):
    """Bottom-sheet drawer after a successful save. dyn=True → x-dc holes for the canvas prototype."""
    rows = []
    k = 0
    p0 = POOL[0]
    rows.append(pick_item(c, p0, 0 in sel, 0, ('{{v.c0}}', '{{v.t0}}') if dyn else None))
    for src, title in SECTIONS:
        items = [p for p in POOL if p['src'] == src]
        if not history and src != 'other':
            continue
        rows.append(f'<div class="pk-sec" {ds(ds="Section header", visible_if="section has ≥1 matching ad (PM/BE define)")}>{T("span", "header-caption", "text-secondary", title)}</div>')
        for p in items:
            k += 1
            rows.append(pick_item(c, p, p['id'] in sel, k * 25, ('{{v.c%d}}' % p['id'], '{{v.t%d}}' % p['id']) if dyn else None))
    n = len(sel)
    if dyn:
        cta_txt, cta_dis, cta_cls, cta_state = 'So sánh ({{v.n}}/4)', '', '{{v.ctaCls}}', '{{v.ctaState}}'
        cta_tap, close_tap, link_tap = 'onClick="{{v.compare}}"', 'onClick="{{v.close}}"', 'onClick="{{v.goSaved}}"'
    else:
        cta_txt = 'So sánh (%d/4)' % n
        cta_dis = 'disabled' if n < 2 else ''
        cta_cls, cta_state = cta_bump, 'Disabled' if n < 2 else 'Active'
        cta_tap, close_tap, link_tap = 'data-act="compare"', 'data-act="close"', 'data-act="saved"'
    dis_attr = 'aria-disabled="{{v.ctaOff}}"' if dyn else cta_dis
    return f'''
<div class="sheet {'closing' if closing else ''}" role="dialog" aria-modal="true" aria-labelledby="sh-title" {ds(ds='Drawer', screen='save-compare-drawer', surface='bottom-sheet', dismiss='tap scrim | Đóng | swipe down | Android back', radius='radius-modal (top only)', raw='no header close icon + 2-button footer — product decision, deviates from drawer.md intentional')}>
  <div class="sh-grab" {REF}></div>
  <div class="sh-head" {ds(pad='padding-small-12 padding-medium-16', gap='gap-x-small-8')}>
    {icon('CircleCheck-fill', 24, 'c-text-success', ds(icon='CircleCheck-fill', color='text-success'))}
    {T('h2', 'header-section', 'text-primary', 'Đã lưu thành công', 'sh-title', 'id="sh-title"')}
    <button class="sh-link ty-label-section c-text-primary" {link_tap} {ds(ds='Text link', typo='label-section', color='text-primary', on_tap='open Saved ads page', raw='underline intentional')}>Xem tất cả</button>
  </div>
  <div class="sh-body" {ds(ds='Drawer body', raw='max 10 recommended ads; just-saved ad pinned on top, preselected')}>
    {''.join(rows)}
  </div>
  <div class="sh-foot" {ds(gap='gap-x-small-8', pad='padding-small-12 padding-medium-16', raw='width split 30/70 intentional')}>
    <button class="btn btn-ter" {close_tap} {ds(ds='Button', type='Tertiary', size='L-40', state='Active', pill='false', typo='label-page', color='text-primary')}>Đóng</button>
    <button class="btn btn-pri cta {cta_cls}" {cta_tap} {dis_attr} {ds(ds='Button', type='Primary', size='L-40', state=cta_state, pill='false', typo='label-page', color='text-on-background', visible_if='disabled when selected < 2')}>{cta_txt}</button>
  </div>
</div>'''


def drawer_skeleton():
    row = '''<div class="pk-item sk" aria-hidden="true"><span class="sk-b sk-cb"></span><span class="sk-b sk-th"></span><span class="pk-tx"><span class="sk-b sk-l1"></span><span class="sk-b sk-l2"></span><span class="sk-b sk-l3"></span></span></div>'''
    return f'''
<div class="sheet" {ds(ds='Drawer', surface='bottom-sheet', state='Skeleton', raw='skeleton while recommendations load; just-saved ad renders immediately')}>
  <div class="sh-grab" {REF}></div>
  <div class="sh-head">{icon('CircleCheck-fill', 24, 'c-text-success', ds(icon='CircleCheck-fill', color='text-success'))}{T('h2', 'header-section', 'text-primary', 'Đã lưu thành công', 'sh-title')}<span class="sh-link ty-label-section c-text-primary">Xem tất cả</span></div>
  <div class="sh-body" {ds(ds='Skeleton', bg='skeleton-background')}>{row * 5}</div>
  <div class="sh-foot"><button class="btn btn-ter" {ds(ds='Button', type='Tertiary', size='L-40', state='Active', pill='false')}>Đóng</button><button class="btn btn-pri" disabled {ds(ds='Button', type='Primary', size='L-40', state='Disabled', pill='false')}>So sánh (1/4)</button></div>
</div>'''


def snackbar(msg, action='', dyn=False, above_sheet=True, hidden=False):
    act = ''
    if dyn:
        act = '<sc-if value="{{v.snAct}}" hint-placeholder-val="{{false}}"><button class="snack-act ty-label-section c-text-blank" onClick="{{v.snGo}}">{{v.snActT}}</button></sc-if>'
        msg = '{{v.snMsg}}'
    elif action:
        act = f'<button class="snack-act ty-label-section c-text-blank" data-act="saved" {ds(typo="label-section", color="text-blank", on_tap="open Saved ads page")}>{action}</button>'
    cls = ('up ' if above_sheet else '') + ('{{v.snCls}}' if dyn else ('' if hidden else 'show'))
    return f'''<div class="snack {cls}" role="status" aria-live="polite" {ds(ds='?? confirm (Snackbar — not in DS component list)', bg='background-inverted', radius='radius-card-small', pad='padding-small-12 padding-medium-16', raw='full width minus 16px gutters; 2s, 4s with action intentional')}>{T('span', 'body-section', 'text-blank', msg, 'snack-msg')}{act}</div>'''


# ---------------------------------------------------------------- compare screen (new — handoff scope)
def compare(c, sel, dyn=False, proto=False):
    """proto=True: every column + every tag/remove button rendered with ids, JS filters (repo prototype)."""
    ids = [p['id'] for p in POOL] if (dyn or proto) else sorted(sel)
    items = {p['id']: p for p in POOL}
    shown = [items[i] for i in ids]
    wide = len(sel) > 2
    min_ppm = min(items[i]['ppm'] for i in sel)

    def wrap(i, html):
        return ('<sc-if value="{{v.k%d}}" hint-placeholder-val="{{%s}}">%s</sc-if>' % (i, 'true' if i in sel else 'false', html)) if dyn else html

    cols = []
    for p in shown:
        rm = ''
        rm_btn = f'''<button class="cmp-rm" aria-label="Bỏ tin khỏi so sánh" {'onClick="{{v.rm%d}}"' % p['id'] if dyn else 'data-rm="%d"' % p['id']} {ds(ds='Icon Button', type='Ghost', size='M-32', state='Active', pill='true', icon='Close-outline', visible_if='compared ads > 2', raw='48px hit area via ::after intentional')}>{icon('Close-outline', 20)}</button>'''
        if dyn:
            rm = '<sc-if value="{{v.canRm}}" hint-placeholder-val="{{%s}}">%s</sc-if>' % ('true' if wide else 'false', rm_btn)
        elif wide or proto:
            rm = rm_btn
        cols.append(wrap(p['id'], f'''<div class="cmp-col" data-col="{p['id']}"><div class="cmp-im">{c.tag(p['img'], 280, 'cmp-img', ds(radius='radius-card-small'))}{rm}</div>{T('p', 'body-section', 'text-primary', escape(p['title']), 'cmp-ttl', ds(content_rule='max-2-lines, ellipsis'))}</div>'''))
    body = []
    labels = {'price': 'Giá', 'ppm': 'Đơn giá', 'area': 'Diện tích', 'legal': 'Pháp lý', 'type': 'Loại hình', 'bed': 'Phòng ngủ', 'wc': 'Phòng vệ sinh', 'furn': 'Nội thất', 'floors': 'Số tầng', 'dir': 'Hướng'}
    for title, keys in CMP_SECTIONS:
        body.append(f'<div class="cmp-sec">{T("span", "header-caption", "text-primary", title)}</div>')
        for key in keys:
            cells = []
            for p in shown:
                if key == 'ppm':
                    tag = f'<span class="tag-best ty-label-annotation c-text-success" {ds(ds="Tag", bg="background-success-light", color="text-success", typo="label-annotation", visible_if="lowest tr/m² among compared ads")}>Rẻ nhất</span>'
                    if dyn:
                        tag = '<sc-if value="{{v.b%d}}" hint-placeholder-val="{{%s}}">%s</sc-if>' % (p['id'], 'true' if p['ppm'] == min_ppm else 'false', tag)
                    elif proto:
                        tag = tag.replace('<span class="tag-best', '<span data-best="%d" class="tag-best' % p['id'])
                    elif not (p['ppm'] == min_ppm and len(sel) > 1):
                        tag = ''
                    inner = T('span', 'body-section', 'text-primary', fmt_ppm(p['ppm'])) + tag
                elif key == 'price':
                    inner = T('b', 'label-section', 'text-brand', p['price'])
                else:
                    v = p[key]
                    inner = T('span', 'body-section', 'text-primary', v) if v else T('span', 'body-section', 'text-tertiary', '---', '', ds(content_rule='missing value → ---'))
                cid = (' data-cell="%d"' % p['id']) if proto else ''
                cells.append(wrap(p['id'], f'<div class="cmp-cell"{cid}>{inner}</div>'))
            body.append(f'<div class="cmp-row"><span class="cmp-lbl ty-body-caption c-text-secondary" {ds(typo="body-caption", color="text-secondary")}>{labels[key]}</span><div class="cmp-cells">{"".join(cells)}</div></div>')
    width_cls = '{{v.cw}}' if dyn else ('wn' if wide else 'w2')
    back = 'onClick="{{v.back}}"' if dyn else 'data-act="back"'
    count = '{{v.cmpN}}' if dyn else str(len(sel))
    return f'''
<div class="cmp {width_cls}" {ds(screen='compare-pty', surface='page', raw='2 ads → 2 equal columns 187.5px; >2 → 140px columns, horizontal scroll intentional')}>
  <div class="cmp-head">
    <button class="cmp-back" aria-label="Quay lại" {back} {ds(ds='Icon Button', type='Ghost', size='XL-48', state='Active', pill='false', icon='Arrowleft-outline', on_tap='back to drawer (selection kept)')}>{icon('Arrowleft-outline')}</button>
    {T('h1', 'header-section', 'text-primary', 'So sánh tin (' + count + ')')}
  </div>
  <div class="cmp-scroll"><div class="cmp-tbl">
    <div class="cmp-cols">{''.join(cols)}</div>
    {''.join(body)}
  </div></div>
</div>'''


# ---------------------------------------------------------------- iPhone frame
STATUS = '''<div class="ios-statusbar" data-ds-context="reference"><span>9:41</span><span class="icons"><svg width="18" height="12" viewBox="0 0 18 12" fill="none"><rect y="7" width="3" height="5" rx="1" fill="currentColor"/><rect x="5" y="5" width="3" height="7" rx="1" fill="currentColor"/><rect x="10" y="2.5" width="3" height="9.5" rx="1" fill="currentColor"/><rect x="15" width="3" height="12" rx="1" fill="currentColor"/></svg><svg width="17" height="12" viewBox="0 0 17 12" fill="none"><path d="M8.5 2.7c2.4 0 4.6.9 6.3 2.5l1.6-1.7C14.3 1.5 11.5.3 8.5.3S2.7 1.5.6 3.5l1.6 1.7C3.9 3.6 6.1 2.7 8.5 2.7Zm0 4.1c1.3 0 2.5.5 3.4 1.4l1.7-1.7c-1.4-1.3-3.2-2.1-5.1-2.1s-3.7.8-5.1 2.1l1.7 1.7c.9-.9 2.1-1.4 3.4-1.4Zm2 3.4L8.5 12l-2-1.8c.5-.6 1.2-.9 2-.9s1.5.3 2 .9Z" fill="currentColor"/></svg><svg width="25" height="12" viewBox="0 0 25 12" fill="none"><rect x=".5" y=".5" width="21" height="11" rx="3" stroke="currentColor" stroke-opacity=".4"/><rect x="2" y="2" width="15" height="8" rx="1.6" fill="currentColor"/><path d="M23.5 4v4c.8-.3 1.3-1.1 1.3-2s-.5-1.7-1.3-2Z" fill="currentColor" fill-opacity=".4"/></svg></span></div>'''


def phone(content, overlay='', label='', note='', touch=None, pid='', screen='adview-pty', insert='overlay:after-tap(Lưu)'):
    """content scrolls inside .app-scroll; overlay (scrim/drawer/snackbar) sits on .iphone-screen, above the scroll."""
    t = f'<span class="touch" style="left:{touch[0]}px;top:{touch[1]}px"></span>' if touch else ''
    cap = f'<div class="ph-cap"><b>{label}</b><span>{note}</span></div>' if label else ''
    return f'''
<figure class="ph" {('id="%s"' % pid) if pid else ''}>
  {cap}
  <div class="iphone" {REF}>
    <div class="iphone-screen">
      <div class="dynamic-island" {REF}></div>
      <div class="app-scroll" {ds(screen=screen, platform='app', vertical='PTY', surface='page', size='375x788', mode='partial', insert=insert)}>
        {STATUS}
        {content}
      </div>
      {overlay}
      <div class="home-indicator" {REF}></div>
      {t}
    </div>
  </div>
</figure>'''


def scrim(dyn=False, closing=False):
    tap = 'onClick="{{v.close}}"' if dyn else 'data-act="close"'
    return f'<div class="scrim {"closing" if closing else ""}" {tap} {ds(bg="background-overlay", on_tap="close drawer (slide down 260ms)")}></div>'


def compare_page(c, sel):
    return phone(compare(c, sel), screen='compare-pty', insert='new page')


# ---------------------------------------------------------------- CSS
CSS = r'''
:root{
  /* Nhà Tốt theme — references/brands/chotot-nhatot.md + components/tokens.md (PTY) */
  --background-primary:#ffffff; --background-app:#f7f7f7; --background-secondary:#f4f4f4; --background-tertiary:#e8e8e8;
  --background-brand:#fa6819; --background-success:#12a154; --background-success-light:#ecf9f1;
  --background-inverted:#222222; --background-overlay:rgba(34,34,34,0.5);
  --text-primary:#222222; --text-secondary:#595959; --text-tertiary:#8c8c8c; --text-link:#306bd9; --text-brand:#c74e0e;
  --text-success:#12a154; --text-disabled:#c0c0c0; --text-blank:#ffffff; --text-on-background:#ffffff;
  --border-divider:#f4f4f4; --border-thin:#e8e8e8; --border-regular:#dddddd; --border-black:#222222; --border-active:#fa6819; --border-brand:#fa6819;
  --icon-primary:#222222; --icon-secondary:#595959; --icon-brand:#fa6819; --icon-blank:#ffffff; --icon-disabled:#c0c0c0;
  --interaction-brand-hover:#fb8f4a; --interaction-brand-pressed:#e05a10; --interaction-primary-hover:#f4f4f4;
  --interaction-neutral-light-pressed:#dddddd; --interaction-brand-light-pressed:#fa6819;
  --button-disabled:#c0c0c0; --button-blank:#ffffff;
  --skeleton-background:#f4f4f4; --skeleton-item:#e8e8e8;
  --gap-2x-small-4:4px; --gap-x-small-8:8px; --gap-small-12:12px;
  --padding-2x-small-4:4px; --padding-x-small-8:8px; --padding-small-12:12px; --padding-medium-16:16px;
  --radius-ad-small:4px; --radius-card-small:8px; --radius-card:12px; --radius-modal:20px; --radius-pill:999px;
  --stroke-divider:1px; --stroke-action:2px;
  --shadow-floating:0px 4px 16px 0px rgba(34,34,34,0.12);
  --font-family:'Reddit Sans',-apple-system,BlinkMacSystemFont,sans-serif;
  /* motion (prototype-to-spec) */
  --ease-out:cubic-bezier(.2,.8,.2,1); --ease-pop:cubic-bezier(.3,1.6,.5,1);
}
*{margin:0;padding:0;box-sizing:border-box}
[hidden]{display:none!important}
button{font:inherit;border:0;background:none;cursor:pointer;color:inherit}
/* typography tokens */
.ty-display-annotation{font-size:18px;font-weight:700;line-height:26px}
.ty-header-section{font-size:16px;font-weight:600;line-height:24px}
.ty-header-caption{font-size:14px;font-weight:600;line-height:20px}
.ty-label-page{font-size:16px;font-weight:700;line-height:24px}
.ty-label-section{font-size:14px;font-weight:700;line-height:20px}
.ty-label-annotation{font-size:10px;font-weight:700;line-height:16px}
.ty-body-section{font-size:14px;font-weight:400;line-height:20px}
.ty-body-caption{font-size:12px;font-weight:400;line-height:18px}
.c-text-primary{color:var(--text-primary)} .c-text-secondary{color:var(--text-secondary)} .c-text-tertiary{color:var(--text-tertiary)}
.c-text-brand{color:var(--text-brand)} .c-text-success{color:var(--text-success)} .c-text-blank{color:var(--text-blank)}
.c-icon-brand{color:var(--icon-brand)} .c-icon-secondary{color:var(--icon-secondary)}
.ds-icon{width:24px;height:24px;flex:none;color:var(--icon-primary);vertical-align:middle}
.ds-icon--20{width:20px;height:20px} .ds-icon--16{width:16px;height:16px}
.ds-icon.c-text-success{color:var(--text-success)} .ds-icon.c-icon-brand{color:var(--icon-brand)} .ds-icon.c-icon-secondary{color:var(--icon-secondary)}

/* iPhone 14 Pro frame — references/iphone-frame.md (presentation chrome, reference only) */
.iphone{position:relative;width:393px;height:806px;flex-shrink:0;background:#1c1c1e;border-radius:56px;padding:9px;box-shadow:0 0 0 2px #3a3a3c,0 24px 60px rgba(0,0,0,.35)}
.iphone-screen{position:relative;width:375px;height:788px;border-radius:47px;overflow:hidden;background:var(--background-primary);font-family:var(--font-family);color:var(--text-primary)}
.dynamic-island{position:absolute;top:11px;left:50%;transform:translateX(-50%);width:120px;height:34px;background:#000;border-radius:20px;z-index:9999}
.app-scroll{position:absolute;inset:0;overflow-y:auto;overflow-x:hidden;display:flex;flex-direction:column;scrollbar-width:none}
.app-scroll::-webkit-scrollbar{display:none}
.ios-statusbar{position:sticky;top:0;z-index:20;height:50px;flex-shrink:0;display:flex;align-items:flex-end;justify-content:space-between;padding:0 26px 7px 32px;background:var(--background-primary);color:var(--text-primary);font-size:14px;font-weight:600}
.ios-statusbar .icons{display:flex;gap:5px;align-items:center}
.home-indicator{position:absolute;left:50%;bottom:8px;transform:translateX(-50%);z-index:9998;width:134px;height:5px;border-radius:3px;background:rgba(0,0,0,.85)}

/* host AdView — reference */
.host{display:flex;flex-direction:column;flex:1;min-height:738px;background:var(--background-primary)}
.host-hero{position:relative;height:250px;flex:none;background:var(--background-tertiary)}
.host-im{width:100%;height:100%;object-fit:cover;display:block}
.host-nav{position:absolute;left:8px;right:8px;top:8px;display:flex;gap:4px}
.host-ib{width:40px;height:40px;border-radius:var(--radius-pill);background:var(--background-primary);display:grid;place-items:center}
.host-sp{flex:1}
.host-body{padding:var(--padding-small-12) var(--padding-medium-16);display:flex;flex-direction:column;gap:var(--gap-x-small-8);flex:1}
.host-price{display:flex;gap:6px;align-items:baseline}
.host-loc{display:flex;gap:4px;align-items:center}
.host-ph{height:12px;border-radius:var(--radius-ad-small);background:var(--skeleton-background);margin-top:6px}
.host-ph.s{width:60%} .host-ph.m{width:80%}
.host-bar{position:sticky;bottom:0;display:flex;gap:var(--gap-x-small-8);padding:var(--padding-x-small-8) var(--padding-medium-16) 26px;background:var(--background-primary);border-top:var(--stroke-divider) solid var(--border-thin)}
.host-save,.host-btn{height:40px;border-radius:var(--radius-card-small);display:flex;align-items:center;justify-content:center;gap:var(--gap-2x-small-4);padding:0 var(--padding-small-12)}
.host-save{background:var(--button-blank);border:var(--stroke-divider) solid var(--border-regular);color:var(--text-primary);min-width:92px;transition:background .15s}
.host-save:hover{background:var(--interaction-primary-hover)} .host-save:active{background:var(--interaction-neutral-light-pressed)}
.host-save.on .save-ic{color:var(--icon-brand)}
.host-save .save-ic{transition:transform .2s var(--ease-pop)} .host-save.on .save-ic{transform:scale(1.08)}
.host-btn{flex:1} .host-btn.sec{background:var(--background-secondary)} .host-btn.pri{background:var(--background-brand);color:var(--text-on-background)}
.host-btn.pri .ds-icon{color:var(--icon-blank)}

/* scrim + drawer */
.scrim{position:absolute;inset:0;z-index:40;background:var(--background-overlay);animation:fadein .26s var(--ease-out) both}
.scrim.closing{animation:fadeout .26s var(--ease-out) both}
.sheet{position:absolute;left:0;right:0;bottom:0;z-index:41;max-height:640px;display:flex;flex-direction:column;background:var(--background-primary);border-radius:var(--radius-modal) var(--radius-modal) 0 0;box-shadow:var(--shadow-floating);animation:sheetup .3s var(--ease-out) both}
.sheet.closing{animation:sheetdown .26s var(--ease-out) both}
.sh-grab{width:36px;height:4px;border-radius:var(--radius-pill);background:var(--border-regular);margin:8px auto 0;flex:none}
.sh-head{display:flex;align-items:center;gap:var(--gap-x-small-8);padding:var(--padding-small-12) var(--padding-medium-16);border-bottom:var(--stroke-divider) solid var(--border-thin);flex:none}
.sh-title{flex:1}
.sh-link{text-decoration:underline;text-underline-offset:2px;min-height:48px;padding:0 4px;margin-right:-4px}
.sh-body{overflow-y:auto;flex:1;scrollbar-width:none;padding-bottom:var(--padding-x-small-8)}
.sh-body::-webkit-scrollbar{display:none}
.pk-sec{display:flex;align-items:center;min-height:36px;padding:var(--padding-small-12) var(--padding-medium-16) var(--padding-2x-small-4);border-top:8px solid var(--background-secondary);margin-top:var(--padding-x-small-8)}
.pk-item{display:flex;align-items:center;gap:var(--gap-small-12);padding:var(--padding-small-12) var(--padding-medium-16);cursor:pointer;transition:background .15s,transform .12s;animation:cbenter .24s var(--ease-out) both;animation-delay:var(--d,0ms);outline:none}
.pk-item:hover{background:var(--interaction-primary-hover)}
.pk-item:active{transform:scale(.98)}
.pk-item:focus-visible{box-shadow:inset 0 0 0 2px var(--border-active)}
.pk-th{display:block;width:64px;height:64px;border-radius:var(--radius-card-small);object-fit:cover;flex:none}
.pk-tx{display:flex;flex-direction:column;gap:2px;min-width:0;flex:1}
.pk-ttl{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pk-pr{display:flex;gap:6px;align-items:baseline;flex-wrap:wrap}
.pk-sub{display:flex;gap:4px;align-items:center}
/* Checkbox — components/checkbox.md (Standard), PTY brand; motion kept */
.cb{width:24px;height:24px;display:grid;place-items:center;flex:none}
.cb-box{width:20px;height:20px;border-radius:var(--radius-ad-small);border:var(--stroke-action) solid var(--border-regular);background:var(--background-primary);display:grid;place-items:center;transition:background .15s,border-color .15s}
.cb-box .ds-icon{color:var(--icon-blank);opacity:0;transform:scale(.4);transition:opacity .15s,transform .2s var(--ease-pop)}
.pk-item:hover .cb-box{border-color:var(--border-black);background:var(--background-tertiary)}
.pk-item:active .cb-box{background:var(--interaction-brand-light-pressed);border-color:var(--border-brand)}
.pk-item.on .cb-box{background:var(--background-brand);border-color:var(--background-brand);animation:cbpop .22s var(--ease-pop)}
.pk-item.on:hover .cb-box{background:var(--interaction-brand-hover);border-color:var(--interaction-brand-hover)}
.pk-item.on .cb-box .ds-icon{opacity:1;transform:scale(1)}
.sh-foot{display:flex;gap:var(--gap-x-small-8);padding:var(--padding-small-12) var(--padding-medium-16) 26px;border-top:var(--stroke-divider) solid var(--border-thin);background:var(--background-primary);flex:none}
/* Button — components/button.md, L-40, not pill */
.btn{height:40px;border-radius:var(--radius-card-small);padding:var(--padding-2x-small-4) var(--padding-small-12);font-size:16px;font-weight:700;line-height:24px;display:flex;align-items:center;justify-content:center;transition:background .15s,color .15s}
.btn-ter{flex:3;background:var(--button-blank);border:var(--stroke-divider) solid var(--border-regular);color:var(--text-primary)}
.btn-ter:hover{background:var(--interaction-primary-hover)} .btn-ter:active{background:var(--interaction-neutral-light-pressed)}
.btn-pri{flex:7;background:var(--background-brand);color:var(--text-on-background)}
.btn-pri:hover{background:var(--interaction-brand-hover)} .btn-pri:active{background:var(--interaction-brand-pressed)}
.btn-pri:disabled,.btn-pri.off{background:var(--button-disabled);color:var(--text-blank);cursor:default}
.btn:focus-visible,.sh-link:focus-visible,.cmp-back:focus-visible,.cmp-rm:focus-visible,.snack-act:focus-visible{outline:2px solid var(--border-active);outline-offset:2px}
.cta.bmpA{animation:ctabumpA .2s var(--ease-pop)} .cta.bmpB{animation:ctabumpB .2s var(--ease-pop)}
/* skeleton */
.sk{cursor:default;animation:none} .sk:hover{background:none}
.sk-b{display:block;background:var(--skeleton-item);border-radius:var(--radius-ad-small);animation:pulse 1.2s ease-in-out infinite}
.sk-cb{width:20px;height:20px;margin:2px} .sk-th{width:64px;height:64px;border-radius:var(--radius-card-small)}
.sk-l1{height:14px;width:90%} .sk-l2{height:14px;width:60%;margin-top:6px} .sk-l3{height:10px;width:40%;margin-top:6px}
/* snackbar */
.snack{position:absolute;left:16px;right:16px;bottom:34px;z-index:60;display:flex;align-items:center;gap:var(--gap-small-12);min-height:48px;padding:var(--padding-small-12) var(--padding-medium-16);border-radius:var(--radius-card-small);background:var(--background-inverted);opacity:0;transform:translateY(12px);pointer-events:none;transition:opacity .2s,transform .2s var(--ease-out)}
.snack.up{bottom:92px}
.snack.show{opacity:1;transform:none;pointer-events:auto}
.snack-msg{flex:1}
.snack-act{text-decoration:underline;text-underline-offset:2px;min-height:44px;white-space:nowrap}
/* compare */
.cmp{display:flex;flex-direction:column;flex:1;background:var(--background-primary);animation:slidein .3s var(--ease-out) both}
.cmp-head{position:sticky;top:50px;z-index:5;display:flex;align-items:center;height:48px;padding-right:var(--padding-medium-16);background:var(--background-primary);border-bottom:var(--stroke-divider) solid var(--border-thin)}
.cmp-back{width:48px;height:48px;display:grid;place-items:center}
.cmp-back:hover{background:var(--interaction-primary-hover)}
.cmp-scroll{overflow-x:auto;scrollbar-width:none} .cmp-scroll::-webkit-scrollbar{display:none}
.cmp-tbl{min-width:100%;width:max-content}
.cmp-cols,.cmp-cells{display:flex}
.cmp-col,.cmp-cell{flex:none;width:187.5px;padding:var(--padding-x-small-8) var(--padding-small-12)}
.cmp.wn .cmp-col,.cmp.wn .cmp-cell{width:140px}
.cmp-col+.cmp-col,.cmp-cell+.cmp-cell{border-left:var(--stroke-divider) solid var(--border-thin)}
.cmp-im{position:relative}
.cmp-img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:var(--radius-card-small);display:block}
.cmp-rm{position:absolute;top:4px;right:4px;width:32px;height:32px;border-radius:var(--radius-pill);background:var(--background-primary);display:grid;place-items:center;box-shadow:var(--shadow-floating)}
.cmp-rm::after{content:'';position:absolute;inset:-8px}
.cmp-rm:hover{background:var(--interaction-primary-hover)}
.cmp-ttl{margin-top:6px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.cmp-sec{position:sticky;left:0;width:375px;padding:var(--padding-x-small-8) var(--padding-medium-16);background:var(--background-secondary)}
.cmp-row{border-bottom:var(--stroke-divider) solid var(--border-divider)}
.cmp-lbl{display:block;position:sticky;left:0;width:375px;padding:6px var(--padding-small-12) 0}
.cmp-cell{display:flex;flex-direction:column;align-items:flex-start;gap:2px;padding-top:2px}
.tag-best{display:inline-block;padding:0 6px;border-radius:var(--radius-ad-small);background:var(--background-success-light)}
/* touch-point marker (annotation chrome) */
.touch{position:absolute;z-index:9997;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;border:3px solid var(--border-brand);background:rgba(250,104,25,.15);pointer-events:none}
@keyframes fadein{from{opacity:0}} @keyframes fadeout{to{opacity:0}}
@keyframes sheetup{from{transform:translateY(100%)}} @keyframes sheetdown{to{transform:translateY(100%)}}
@keyframes slidein{from{transform:translateX(24px);opacity:0}}
@keyframes cbpop{0%{transform:scale(.8)}60%{transform:scale(1.12)}100%{transform:scale(1)}}
@keyframes cbenter{from{opacity:0;transform:translateY(6px)}}
@keyframes ctabumpA{50%{transform:scale(1.04)}} @keyframes ctabumpB{50%{transform:scale(1.04)}}
@keyframes pulse{50%{opacity:.5}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:1ms!important;animation-delay:0ms!important;transition-duration:1ms!important}}
'''

PAGE_CSS = r'''
body{background:#dfe1e5;font-family:var(--font-family);color:var(--text-primary);padding:48px 40px 80px}
.pg-h{max-width:1600px;margin:0 auto 32px}
.pg-h h1{font-size:28px;font-weight:600;line-height:36px}
.pg-h p{font-size:16px;line-height:24px;color:var(--text-secondary);margin-top:8px;max-width:960px}
.pg-sec{font-size:20px;font-weight:700;margin:48px auto 20px;max-width:1600px}
.flow{display:flex;gap:48px;flex-wrap:wrap;align-items:flex-start;max-width:1600px;margin:0 auto}
.ph{display:flex;flex-direction:column;gap:12px;position:relative}
.ph-cap{display:flex;flex-direction:column;width:393px}
.ph-cap b{font-size:16px;line-height:24px} .ph-cap span{font-size:14px;line-height:20px;color:var(--text-secondary)}
.flow .ph:not(:last-child)::after{content:'→';position:absolute;right:-38px;top:440px;font-size:28px;color:var(--text-tertiary)}
.flow.edge .ph::after{display:none}
'''


# ---------------------------------------------------------------- flow screens (static)
def flow_screens(c):
    S = []
    S.append(phone(host_adview(c, False), label='1 · Bấm Lưu', note='Tin chưa lưu, bấm “Lưu” ở bottom bar.', touch=(62, 760)))
    S.append(phone(host_adview(c, True), scrim() + drawer(c, sel=(0,)), label='2 · Drawer mặc định', note='Tin vừa lưu ở trên cùng, đã chọn sẵn. CTA disabled khi < 2 tin.', touch=(188, 300)))
    S.append(phone(host_adview(c, True), scrim() + drawer(c, sel=(0, 1, 3)), label='3 · Đã chọn 3 tin', note='CTA “So sánh (3/4)”, bump mỗi lần đổi lựa chọn.', touch=(255, 744)))
    S.append(phone(host_adview(c, True), scrim() + drawer(c, sel=(0, 1, 3, 4)) + snackbar('Chỉ được chọn tối đa 4 tin để so sánh'), label='4 · Đạt tối đa 4 tin', note='Tin còn lại không disable; chạm → snackbar.', touch=(188, 600)))
    S.append(phone(compare(c, (0, 1)), label='5 · So sánh 2 tin', note='2 cột chia đều, không có nút bỏ tin.', screen='compare-pty', insert='new page'))
    S.append(phone(compare(c, (0, 1, 3, 4)), label='6 · So sánh trên 2 tin', note='Cột 140px, cuộn ngang, ✕ để bỏ tin (về 2 thì ẩn ✕).', screen='compare-pty', insert='new page'))
    S.append(phone(host_adview(c, False), snackbar('Đã bỏ lưu.', 'Đến trang Đã lưu', above_sheet=False), label='7 · Bỏ lưu', note='Không mở drawer; snackbar 4s kèm hành động.'))
    E = []
    E.append(phone(host_adview(c, True), scrim() + drawer_skeleton(), label='A1 · Đang tải gợi ý', note='Skeleton cho danh sách; CTA disabled.'))
    E.append(phone(host_adview(c, True), snackbar('Đã lưu tin', 'Xem tin đã lưu', above_sheet=False), label='A2 · Không có tin gợi ý', note='Không mở drawer, chỉ snackbar.'))
    E.append(phone(host_adview(c, True), scrim() + drawer(c, sel=(0,), history=False), label='A3 · Ẩn section trống', note='Chưa có lịch sử → chỉ còn “Tin khác trên Nhà Tốt”.'))
    E.append(phone(host_adview(c, True), scrim() + drawer(c, sel=(1,)), label='A4 · Bỏ chọn tin vừa lưu', note='Được phép; CTA disabled đến khi đủ 2 tin.'))
    return S, E


def sprite():
    with open(os.path.join(HERE, 'ds-symbols.txt'), encoding='utf-8') as f:
        return '<svg style="display:none" aria-hidden="true">' + ''.join(l.strip() for l in f if l.strip()) + '</svg>'


# ---------------------------------------------------------------- repo prototype (vanilla JS)
def repo_proto(c):
    cmp_full = compare(c, (0, 1), proto=True)  # all 7 columns; JS shows the selected ones
    content = f'<div class="pv-host">{host_adview(c, False, "data-act=\"save\"")}</div><div class="pv-cmp" hidden>{cmp_full}</div>'
    overlay = '<div class="pv-ov" hidden>' + scrim() + drawer(c, sel=(0,)) + '</div>' + snackbar('', hidden=True, above_sheet=False)
    return phone(content, overlay, label='Prototype', note='Bấm Lưu → chọn tin → So sánh. Chạm vùng tối / Đóng để đóng drawer.', pid='proto')


PROTO_JS = r'''
(function(){
  var root=document.getElementById('proto'); if(!root) return;
  var $=function(s){return root.querySelector(s)}, $$=function(s){return Array.prototype.slice.call(root.querySelectorAll(s))};
  var ov=$('.pv-ov'), host=$('.pv-host'), cmp=$('.pv-cmp'), snack=$('.snack'), cta=$('.cta'), save=$('.host-save');
  var sel=[0], saved=false, bump='', tt;
  var PPM=%PPM%;
  function toast(msg,act){
    snack.querySelector('.snack-msg').textContent=msg;
    var a=snack.querySelector('.snack-act'); if(a) a.remove();
    if(act){a=document.createElement('button');a.className='snack-act ty-label-section c-text-blank';a.textContent=act;a.setAttribute('data-act','saved');snack.appendChild(a);}
    snack.classList.toggle('up',!ov.hidden); snack.classList.add('show');
    clearTimeout(tt); tt=setTimeout(function(){snack.classList.remove('show')},act?4000:2000);
  }
  function paint(){
    $$('.pk-item[data-id]').forEach(function(el){var on=sel.indexOf(+el.dataset.id)>=0;el.classList.toggle('on',on);el.setAttribute('aria-checked',on)});
    cta.textContent='So sánh ('+sel.length+'/4)'; cta.disabled=sel.length<2;
    cta.setAttribute('data-ds-state',sel.length<2?'Disabled':'Active');
    cta.classList.remove('bmpA','bmpB'); if(bump) cta.classList.add(bump);
  }
  function setSaved(v){
    saved=v; save.classList.toggle('on',v); save.setAttribute('aria-pressed',v);
    save.querySelector('use').setAttribute('href',v?'#ds-Heart-fill':'#ds-Heart-outline');
    save.querySelector('span').textContent=v?'Đã lưu':'Lưu';
  }
  function openSheet(){
    sel=[0]; bump=''; paint(); ov.hidden=false;
    ov.querySelectorAll('.scrim,.sheet').forEach(function(e){e.classList.remove('closing')});
    // restart enter stagger
    $$('.pk-item').forEach(function(e){e.style.animation='none';e.offsetHeight;e.style.animation=''});
  }
  function closeSheet(){
    ov.querySelectorAll('.scrim,.sheet').forEach(function(e){e.classList.add('closing')});
    setTimeout(function(){ov.hidden=true},260);
  }
  function toggle(id){
    var i=sel.indexOf(id); bump=bump==='bmpA'?'bmpB':'bmpA';
    if(i>=0){sel.splice(i,1);paint();return}
    if(sel.length>=4){bump='';toast('Chỉ được chọn tối đa 4 tin để so sánh');return}
    sel.push(id); paint();
  }
  var shown=[];
  function paintCmp(){
    var wide=shown.length>2, min=Math.min.apply(null,shown.map(function(i){return PPM[i]}));
    var c=cmp.querySelector('.cmp'); c.classList.toggle('wn',wide); c.classList.toggle('w2',!wide);
    $$('.pv-cmp [data-col]').forEach(function(el){el.hidden=shown.indexOf(+el.dataset.col)<0});
    $$('.pv-cmp [data-cell]').forEach(function(el){el.hidden=shown.indexOf(+el.dataset.cell)<0});
    $$('.pv-cmp .cmp-rm').forEach(function(el){el.hidden=!wide});
    if(!wide) cmp.querySelector('.cmp-scroll').scrollLeft=0;
    $$('.pv-cmp .tag-best').forEach(function(el){el.hidden=PPM[+el.dataset.best]!==min||shown.length<2});
    c.querySelector('h1').textContent='So sánh tin ('+shown.length+')';
  }
  root.addEventListener('click',function(e){
    var t=e.target.closest('[data-act],[data-id],[data-rm]'); if(!t||!root.contains(t)) return;
    if(t.dataset.id!==undefined){toggle(+t.dataset.id);return}
    if(t.dataset.rm!==undefined){shown=shown.filter(function(i){return i!==+t.dataset.rm});paintCmp();return}
    var a=t.dataset.act;
    if(a==='save'){ if(!saved){setSaved(true);openSheet()} else {setSaved(false);toast('Đã bỏ lưu.','Đến trang Đã lưu')} }
    else if(a==='close') closeSheet();
    else if(a==='saved') toast('Đang mở trang Đã lưu…');
    else if(a==='compare'){ if(sel.length<2) return; shown=sel.slice().sort(function(a,b){return a-b}); ov.hidden=true; host.hidden=true; cmp.hidden=false; snack.classList.remove('show'); paintCmp(); root.querySelector('.app-scroll').scrollTop=0 }
    else if(a==='back'){ cmp.hidden=true; host.hidden=false; ov.hidden=false; ov.querySelectorAll('.scrim,.sheet').forEach(function(e){e.classList.remove('closing')}); paint() }
  });
  root.addEventListener('keydown',function(e){
    if((e.key===' '||e.key==='Enter')&&e.target.matches('.pk-item[data-id]')){e.preventDefault();toggle(+e.target.dataset.id)}
    if(e.key==='Escape'&&!ov.hidden) closeSheet();
  });
})();
'''


def build_index(c):
    S, E = flow_screens(c)
    proto = repo_proto(c)
    ppm = json.dumps({p['id']: p['ppm'] for p in POOL})
    imgcss = c.css()
    return f'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lưu tin → So sánh · Nhà Tốt</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Reddit+Sans:wght@400;500;600;700&display=swap">
<style>{CSS}{PAGE_CSS}{imgcss}</style>
</head>
<body>
{sprite()}
<header class="pg-h" {REF}>
  <h1>Promote Compare PTY ad — Lưu tin → So sánh</h1>
  <p>Partial scope trên AdView Nhà Tốt: chỉ drawer “Đã lưu thành công”, snackbar và màn So sánh là phần bàn giao. AdView + khung iPhone là ngữ cảnh (data-ds-context="reference"). Spec-ready: mọi component / text / icon mang data-ds-*.</p>
</header>
<h2 class="pg-sec" {REF}>Prototype tương tác</h2>
<div class="flow edge">{proto}</div>
<h2 class="pg-sec" {REF}>Flow chính</h2>
<div class="flow">{''.join(S)}</div>
<h2 class="pg-sec" {REF}>Edge cases · Drawer</h2>
<div class="flow edge">{''.join(E)}</div>
<script>{PROTO_JS.replace('%PPM%', ppm)}</script>
</body>
</html>'''


# ---------------------------------------------------------------- canvas boards (x-dc)
def dc_doc(title, body, logic, props=None):
    p = (" data-props='%s'" % json.dumps(props, ensure_ascii=False)) if props else ''
    return f'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Reddit+Sans:wght@400;500;600;700&amp;display=swap">
<style>{CSS}{PAGE_CSS}
body{{padding:0;background:transparent}}
.board{{background:#dfe1e5;padding:64px}}
</style>
</helmet>
{body}
</x-dc>
<script type="text/x-dc" data-dc-script{p}>
{logic}
</script>
</body>
</html>'''


def canvas_flow(c):
    S, E = flow_screens(c)
    body = f'''<div class="board" style="width:3167px">{sprite()}
<header class="pg-h" style="margin:0 0 32px"><h1>Lưu tin → So sánh · spec-ready (screen-builder-and-prototype)</h1>
<p>Partial scope trên AdView PTY. Drawer, snackbar, màn So sánh = bàn giao; AdView + khung iPhone = reference. Mọi phần tử mang data-ds-* cho /prototype-to-spec.</p></header>
<h2 class="pg-sec" style="margin:0 0 20px">Flow chính</h2>
<div class="flow" style="max-width:none;flex-wrap:nowrap">{''.join(S)}</div>
<h2 class="pg-sec" style="margin:64px 0 20px">Edge cases · Drawer</h2>
<div class="flow edge" style="max-width:none;flex-wrap:nowrap">{''.join(E)}</div>
</div>'''
    return dc_doc('Flow spec-ready — Lưu → So sánh', body, 'class Component extends DCLogic {\n  renderVals() { return {}; }\n}')


PROTO_DC_LOGIC = r'''
class Component extends DCLogic {
  constructor(props) {
    super(props);
    this.state = { saved: false, sheet: false, closing: false, sel: [0], bump: '', cmp: null, removed: {}, sn: '', snAct: '', snOn: false };
    this.timers = [];
  }
  componentWillUnmount() { this.timers.forEach(clearTimeout); clearTimeout(this.tt); }
  toast(msg, act) {
    this.setState({ sn: msg, snAct: act || '', snOn: true });
    clearTimeout(this.tt);
    this.tt = setTimeout(() => this.setState({ snOn: false }), act ? 4000 : 2000);
  }
  close() {
    if (this.state.closing) return;
    this.setState({ closing: true });
    this.timers.push(setTimeout(() => this.setState({ sheet: false, closing: false }), 260));
  }
  toggle(id) {
    const sel = this.state.sel, bump = this.state.bump === 'bmpA' ? 'bmpB' : 'bmpA';
    if (sel.indexOf(id) >= 0) { this.setState({ sel: sel.filter(x => x !== id), bump }); return; }
    if (sel.length >= 4) { this.toast('Chỉ được chọn tối đa 4 tin để so sánh'); return; }
    this.setState({ sel: sel.concat([id]), bump });
  }
  renderVals() {
    const S = this.state, PPM = %PPM%;
    const v = {};
    const n = S.sel.length;
    [0, 1, 2, 3, 4, 5, 6].forEach(id => {
      v['c' + id] = S.sel.indexOf(id) >= 0 ? 'on' : '';
      v['t' + id] = () => this.toggle(id);
    });
    v.n = n; v.ctaOff = n < 2; v.ctaCls = (S.bump || '') + (n < 2 ? ' off' : ''); v.ctaState = n < 2 ? 'Disabled' : 'Active';
    v.close = () => this.close();
    v.goSaved = () => this.toast('Đang mở trang Đã lưu…');
    v.compare = () => { if (n < 2) return; this.setState({ sheet: false, cmp: S.sel.slice().sort((a, b) => a - b), removed: {} }); };
    const shown = (S.cmp || []).filter(id => !S.removed[id]);
    const min = Math.min.apply(null, shown.map(id => PPM[id]));
    [0, 1, 2, 3, 4, 5, 6].forEach(id => {
      v['k' + id] = shown.indexOf(id) >= 0;
      v['b' + id] = shown.length > 1 && PPM[id] === min;
      v['rm' + id] = () => this.setState({ removed: Object.assign({}, S.removed, { [id]: true }) });
    });
    v.canRm = shown.length > 2; v.cw = shown.length > 2 ? 'wn' : 'w2'; v.cmpN = shown.length;
    v.back = () => this.setState({ cmp: null, sheet: true, closing: false });
    v.snMsg = S.sn; v.snAct = !!S.snAct; v.snActT = S.snAct; v.snCls = (S.snOn ? 'show' : '') + (S.sheet ? ' up' : '');
    v.snGo = () => this.toast('Đang mở trang Đã lưu…');
    return {
      v,
      hostOn: !S.cmp, cmpOn: !!S.cmp, sheetOn: S.sheet, closingCls: S.closing ? 'closing' : '',
      saved: S.saved, unsaved: !S.saved,
      toggleSave: () => {
        if (!S.saved) { this.setState({ saved: true, sheet: true, closing: false, sel: [0], bump: '' }); return; }
        this.setState({ saved: false }); this.toast('Đã bỏ lưu.', 'Đến trang Đã lưu');
      }
    };
  }
}
'''


def canvas_proto(c):
    # Host with a save button whose icon/label depend on state → render both variants behind sc-if.
    host_un = host_adview(c, False, 'onClick="{{toggleSave}}"')
    host_sv = host_adview(c, True, 'onClick="{{toggleSave}}"')
    content = ('<sc-if value="{{hostOn}}" hint-placeholder-val="{{true}}">'
               '<sc-if value="{{unsaved}}" hint-placeholder-val="{{true}}">%s</sc-if>'
               '<sc-if value="{{saved}}" hint-placeholder-val="{{false}}">%s</sc-if></sc-if>'
               '<sc-if value="{{cmpOn}}" hint-placeholder-val="{{false}}">%s</sc-if>') % (host_un, host_sv, compare(c, (0, 1), dyn=True))
    sheet = drawer(c, dyn=True).replace('class="sheet "', 'class="sheet {{closingCls}}"')
    sc = scrim(dyn=True).replace('class="scrim "', 'class="scrim {{closingCls}}"')
    overlay = '<sc-if value="{{sheetOn}}" hint-placeholder-val="{{false}}">%s%s</sc-if>%s' % (sc, sheet, snackbar('', dyn=True, above_sheet=False))
    ph = phone(content, overlay)
    body = f'<div class="board" style="padding:0;background:transparent">{sprite()}{ph}</div>'
    ppm = json.dumps({p['id']: p['ppm'] for p in POOL})
    return dc_doc('Prototype spec-ready — Lưu → So sánh', body, PROTO_DC_LOGIC.replace('%PPM%', ppm),
                  {'$preview': {'width': 393, 'height': 806}})


def main():
    out = os.path.join(HERE, 'index.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(build_index(Ctx(inline=True)))
    print('wrote', out, os.path.getsize(out), 'bytes')
    if '--canvas' in sys.argv:
        d = sys.argv[sys.argv.index('--canvas') + 1]
        c = Ctx(inline=False)
        for name, html in (('SkillFlow.dc.html', canvas_flow(c)), ('SkillProto.dc.html', canvas_proto(c))):
            p = os.path.join(d, name)
            with open(p, 'w', encoding='utf-8') as f:
                f.write(html)
            print('wrote', p, os.path.getsize(p), 'bytes')


if __name__ == '__main__':
    main()
