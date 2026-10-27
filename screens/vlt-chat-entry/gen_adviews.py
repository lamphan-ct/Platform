"""Write AdViewV (GDS/VEH, Figma 9545:20431) and AdViewPTY (Figma 10314:18785) components."""
import json
import re
import sys

P = sys.argv[1]
I = json.load(open(sys.argv[2]))


def icon(name, size, color='currentColor', label=None, style=''):
    vb, body = I[name]
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    st = f' style="flex: none; color: {color};{style}"' if color != 'currentColor' or style else ' style="flex: none"'
    return f'<svg width="{size}" height="{size}" viewBox="{vb}" {a11y}{st}>{body}</svg>'


src = open(f'{P}/AdView.dc.html').read()
svgs = re.findall(r'<svg[^>]*>.*?</svg>', src, flags=re.S)
status_icons = svgs[0] + svgs[1]  # signal + battery from the existing ad view
img = svgs[10].replace('width="24" height="24"', 'width="40" height="40"').replace('Ảnh công ty', 'Ảnh tin đăng')

HEAD = '''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
<link rel="stylesheet" href="vlt-tokens.css">
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Reddit+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<style>body{{margin:0}}</style>
</helmet>
'''

TOAST = '''  <sc-if value="{{{{toast}}}}" hint-placeholder-val="{{{{false}}}}">
    <div role="status" class="t-body-section" style="position: absolute; left: 16px; right: 16px; bottom: {bottom}px; display: flex; align-items: center; gap: var(--gap-x-small-8); padding: var(--padding-small-12) var(--padding-medium-16); background: var(--background-inverted); opacity: 0.9; color: var(--text-blank); border-radius: var(--radius-card)">
      <span style="flex: 1; min-width: 0">Tin nhắn đã được gửi thành công</span>
      <button class="t-label-section" onClick="{{{{onView}}}}" style="flex: none; border: 0; background: transparent; padding: 0; color: var(--text-chotot); text-align: right; white-space: nowrap">Xem tin nhắn</button>
    </div>
    <div aria-hidden="true" style="position: absolute; left: 244px; top: {toast_top}px; width: 131px; height: 69px; box-sizing: border-box; border: 2px solid var(--border-active); pointer-events: none"></div>
  </sc-if>
'''

SCRIPT = '''<script type="text/x-dc" data-dc-script data-props='{{"ad":{{"editor":null}},"hot":{{"editor":"boolean","default":false}},"toast":{{"editor":"boolean","default":false}},"onChat":{{"editor":null}},"onView":{{"editor":null}},"$preview":{{"width":375,"height":812}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    const ad = Object.assign({defaults}, this.props.ad || {{}});
{extra}
    return Object.assign({{}}, ad, {{ hot: !!this.props.hot, toast: !!this.props.toast, onChat: this.props.onChat, onView: this.props.onView }}{more});
  }}
}}
</script>
</body>
</html>
'''

home = '''<div style="position: relative; height: 34px; background: var(--background-primary)">
      <div aria-hidden="true" style="position: absolute; left: 50%; bottom: 8px; width: 134px; height: 5px; margin-left: -67px; border-radius: 100px; background: var(--icon-primary)"></div>
    </div>'''

# ---------- GDS / VEH ----------
circle = lambda inner, label: (f'<button aria-label="{label}" style="width: 36px; height: 36px; flex: none; border: 0; padding: 0; display: grid; place-items: center; '
                               f'border-radius: var(--radius-pill); background: var(--background-primary); color: var(--icon-primary)">{inner}</button>')
market = HEAD.format(title='Chi tiết tin · Chợ Tốt / Chợ Tốt Xe') + f'''<div style="position: relative; width: 375px; height: 812px; overflow: hidden; display: flex; flex-direction: column; font-family: 'Reddit Sans', sans-serif; color: var(--text-primary); background: var(--background-primary)">
  <main style="flex: 1; min-height: 0; overflow: hidden">
    <div style="position: relative; height: 357px; display: grid; place-items: center; background: var(--background-tertiary); color: var(--icon-tertiary)">
      {img}
      <span class="t-label-section" style="position: absolute; right: 16px; bottom: 12px; color: var(--text-blank); text-shadow: 0 1px 2px rgba(0,0,0,.4)">{{{{photoCount}}}}</span>
    </div>
    <div style="padding: var(--padding-small-12) var(--padding-medium-16) 0; display: flex; flex-direction: column; gap: var(--gap-x-small-8)">
      <div style="display: flex; gap: var(--gap-medium-16); align-items: flex-start">
        <div style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: var(--gap-2x-small-4)">
          <h1 class="t-display-annotation" style="margin: 0">{{{{title}}}}</h1>
          <span class="t-body-section" style="color: var(--text-secondary)">{{{{subtitle}}}}</span>
        </div>
        <button class="t-label-section h-neutral" aria-label="Lưu tin" style="flex: none; height: 32px; box-sizing: border-box; padding: 0 var(--padding-small-12); display: inline-flex; align-items: center; gap: var(--gap-2x-small-4); border: 1px solid var(--border-regular); border-radius: var(--radius-pill); background: var(--button-blank); color: var(--text-primary)">{icon('Heart-outline', 20)}Lưu</button>
      </div>
      <div style="display: flex; gap: var(--gap-x-small-8); align-items: center; overflow: hidden">
        <span class="t-header-page" style="flex: none; color: var(--text-error)">{{{{price}}}}</span>
        <sc-for list="{{{{tags}}}}" as="t" hint-placeholder-count="3">
          <span class="t-tagline-annotation" style="flex: none; padding: var(--padding-min-2) var(--padding-2x-small-6); border-radius: var(--radius-ad-small); background: var(--background-secondary); color: var(--text-secondary); white-space: nowrap">{{{{t}}}}</span>
        </sc-for>
      </div>
      <div style="margin-top: var(--padding-x-small-8); padding: var(--padding-small-12) var(--padding-medium-16) var(--padding-medium-16); border-radius: var(--radius-card); background: var(--background-secondary); display: flex; flex-direction: column; gap: var(--gap-2x-small-4)">
        <div style="display: flex; gap: var(--gap-2x-small-4); align-items: center">
          <span class="t-header-caption">Khoảng giá thị trường</span>
          {icon('Info-outline', 16, 'var(--icon-primary)')}
        </div>
        <span class="t-body-caption" style="color: var(--text-tertiary)">Theo dữ liệu trong 3 tháng gần nhất</span>
        <div style="position: relative; height: 64px; margin-top: var(--padding-x-small-8)">
          <div style="position: absolute; left: {{{{curLeft}}}}; top: 0; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center">
            <span class="t-label-caption" style="padding: var(--padding-min-2) var(--padding-x-small-8); border-radius: var(--radius-ad-small); background: var(--text-link); color: var(--text-blank); white-space: nowrap">{{{{marketCur}}}}</span>
            <span aria-hidden="true" style="width: 0; height: 0; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid var(--text-link)"></span>
          </div>
          <div style="position: absolute; left: 0; right: 0; top: 34px; height: 4px; border-radius: var(--radius-pill); background: var(--background-primary)"></div>
          <div style="position: absolute; left: 26%; right: 20%; top: 34px; height: 4px; background: var(--text-link)"></div>
          <div aria-hidden="true" style="position: absolute; left: {{{{curLeft}}}}; top: 28px; width: 1px; height: 16px; border-left: 1px dashed var(--icon-tertiary)"></div>
          <span class="t-body-caption" style="position: absolute; left: 26%; top: 44px; transform: translateX(-50%); color: var(--text-secondary); white-space: nowrap">{{{{marketLow}}}}</span>
          <span class="t-body-caption" style="position: absolute; left: 80%; top: 44px; transform: translateX(-50%); color: var(--text-secondary); white-space: nowrap">{{{{marketHigh}}}}</span>
        </div>
      </div>
      <div style="display: flex; gap: var(--gap-x-small-8); align-items: flex-start; padding-top: var(--padding-x-small-8)">
        {icon('Location-outline', 24, 'var(--icon-primary)')}
        <div style="display: flex; flex-direction: column">
          <span class="t-body-section">{{{{location}}}}</span>
          <span class="t-body-section" style="color: var(--text-tertiary)">{{{{location2}}}}</span>
        </div>
      </div>
      <div style="display: flex; gap: var(--gap-x-small-8); align-items: center">
        {icon('Clock-outline', 24, 'var(--icon-primary)')}
        <span class="t-body-section">{{{{time}}}}</span>
      </div>
    </div>
  </main>
  <div style="position: absolute; left: 0; right: 0; top: 0; padding: 0 0 var(--padding-x-small-8); pointer-events: none">
    <div aria-hidden="true" style="height: 32px; display: flex; align-items: center; justify-content: space-between; padding: 0 var(--padding-medium-16) 0 20px; font-size: 14px; color: var(--text-blank)">
      <span>15:05</span>
      <span style="display: flex; gap: 4px; align-items: center">{status_icons}</span>
    </div>
    <div style="display: flex; align-items: center; justify-content: space-between; padding: var(--padding-x-small-8) var(--padding-medium-16); pointer-events: auto">
      {circle(icon('Arrowleft-outline', 24), 'Quay lại')}
      <span style="display: flex; gap: var(--gap-x-small-8)">{circle(icon('Share-outline', 24), 'Chia sẻ')}{circle(icon('Morevertical-fill', 24), 'Thêm')}</span>
    </div>
  </div>
{TOAST.format(bottom=98, toast_top=650)}  <nav style="flex: none; background: var(--background-primary); border-top: 1px solid var(--border-thin)">
    <div style="height: 56px; box-sizing: border-box; display: flex; align-items: center; gap: var(--gap-x-small-8); padding: 0 var(--padding-medium-16)">
      <div style="width: 40px; flex: none; display: flex; flex-direction: column; align-items: center; color: var(--icon-primary)">
        {icon('Heart-outline', 24)}
        <span class="t-body-caption">Lưu</span>
      </div>
      <button class="t-label-page h-neutral" style="flex: 1; height: 40px; border: 0; border-radius: var(--radius-pill); background: var(--background-secondary); color: var(--text-primary)">Gọi</button>
      <button class="t-label-page h-brand" onClick="{{{{onChat}}}}" style="flex: 1.4; height: 40px; border: 0; border-radius: var(--radius-pill); display: inline-flex; align-items: center; justify-content: center; gap: var(--gap-x-small-8); background: var(--button-primary); color: var(--text-on-background)">{icon('Chat-outline', 24)}Chat</button>
    </div>
    {home}
  </nav>
  <sc-if value="{{{{hot}}}}" hint-placeholder-val="{{{{false}}}}">
    <div aria-hidden="true" style="position: absolute; left: 174px; top: 724px; width: 192px; height: 64px; box-sizing: border-box; border: 2px solid var(--border-active); pointer-events: none"></div>
  </sc-if>
</div>
</x-dc>
''' + SCRIPT.format(
    defaults=json.dumps(dict(title='Apple iPhone 14 Pro 128GB Đen Hàn Quốc', subtitle='iPhone 14 Pro • 128 GB', price='12.300.000 đ',
                             tags=['Kèm phụ kiện', 'Có đổi trả', 'Có quà tặng'], marketLow='9,91 triệu', marketHigh='12,12 triệu', marketCur='12,30 triệu', curPct=82,
                             location='Phường 17, Quận Bình Thạnh, Tp Hồ Chí Minh', location2='Phường Gia Định, TP Hồ Chí Minh mới', time='3 phút trước', photoCount='1/6'),
                        ensure_ascii=False),
    extra='', more=", { curLeft: (ad.curPct ?? 82) + '%' }")
open(f'{P}/AdViewV.dc.html', 'w').write(market)

# ---------- PTY ----------
divider = '<span aria-hidden="true" style="width: 1px; height: 16px; flex: none; background: var(--border-regular)"></span>'
pty = HEAD.format(title='Chi tiết tin · Nhà Tốt') + f'''<div style="position: relative; width: 375px; height: 812px; overflow: hidden; display: flex; flex-direction: column; font-family: 'Reddit Sans', sans-serif; color: var(--text-primary); background: var(--background-secondary)">
  <main style="flex: 1; min-height: 0; overflow: hidden; display: flex; flex-direction: column; gap: var(--gap-x-small-8)">
    <div style="flex: none; position: relative; height: 375px; display: grid; place-items: center; background: var(--background-tertiary); color: var(--icon-tertiary)">
      {img}
      <span class="t-label-section" style="position: absolute; right: 16px; bottom: 12px; padding: var(--padding-2x-small-4) var(--padding-small-12); border-radius: var(--radius-pill); background: var(--background-overlay); color: var(--text-blank)">{{{{photoCount}}}}</span>
    </div>
    <section style="flex: none; margin-top: calc(-1 * var(--gap-x-small-8)); padding: var(--padding-small-12) var(--padding-medium-16); background: var(--background-primary); display: flex; flex-direction: column; gap: var(--gap-small-12)">
      <div style="display: flex; flex-direction: column; gap: var(--gap-2x-small-4)">
        <span class="t-label-caption" style="align-self: flex-start; height: 18px; box-sizing: border-box; padding: 1px var(--padding-2x-small-4); display: inline-flex; gap: 2px; align-items: center; border-radius: 5px; background: var(--background-warning); color: var(--text-blank)">{icon('Shieldcheck-fill', 13)}Đối Tác</span>
        <div style="display: flex; gap: var(--gap-medium-16); align-items: flex-start">
          <div style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: var(--gap-2x-small-4)">
            <h1 class="t-display-annotation" style="margin: 0">{{{{title}}}}</h1>
            <div class="t-body-section" style="display: flex; gap: var(--gap-x-small-8); color: var(--text-tertiary); white-space: nowrap; overflow: hidden">
              <sc-for list="{{{{params}}}}" as="p" hint-placeholder-count="3"><span>{{{{p}}}}</span></sc-for>
            </div>
          </div>
          <button class="t-label-section h-neutral" aria-label="Lưu tin" style="flex: none; height: 32px; box-sizing: border-box; padding: var(--padding-2x-small-4) var(--padding-small-12); display: inline-flex; align-items: center; gap: var(--gap-2x-small-4); border: 1px solid var(--border-regular); border-radius: var(--radius-pill); background: var(--button-blank); color: var(--text-primary)">{icon('Heart-outline', 20)}Lưu</button>
        </div>
      </div>
      <div style="display: flex; gap: var(--gap-x-small-8); align-items: center">
        <span class="t-header-page" style="color: var(--text-error)">{{{{price}}}}</span>
        {divider}
        <span class="t-header-caption">{{{{unitPrice}}}}</span>
        {divider}
        <span class="t-header-caption">{{{{area}}}}</span>
      </div>
      <div style="display: flex; gap: var(--gap-x-small-8); align-items: center">
        {icon('Location-outline', 24, 'var(--icon-primary)')}
        <span class="t-body-section" style="flex: 1; min-width: 0">{{{{location}}}}</span>
      </div>
      <div style="display: flex; gap: var(--gap-x-small-8); align-items: center">
        {icon('Building-outline', 24, 'var(--icon-primary)')}
        <span class="t-body-section" style="flex: 1; min-width: 0">Dự án: <b class="t-header-caption" style="color: var(--text-link)">{{{{project}}}}</b></span>
      </div>
      <div style="display: flex; gap: var(--gap-x-small-8); align-items: center">
        {icon('Clock-outline', 24, 'var(--icon-primary)')}
        <span class="t-body-section" style="flex: 1; min-width: 0">{{{{time}}}}</span>
      </div>
    </section>
    <section style="flex: none; margin: 0 var(--padding-x-small-8); padding: var(--padding-small-12); border-radius: var(--radius-card-small); background: var(--background-primary); display: flex; flex-direction: column; gap: var(--gap-x-small-8)">
      <h2 class="t-label-page" style="margin: 0">Đặc điểm bất động sản</h2>
      <div style="display: flex; flex-direction: column">
        <sc-for list="{{{{features}}}}" as="f" hint-placeholder-count="5">
          <div style="display: flex; gap: var(--gap-x-small-8); align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border-divider)">
            {icon('Note-outline', 20, 'var(--icon-primary)')}
            <span class="t-body-section" style="flex: 1; max-width: 180px">{{{{f.label}}}}</span>
            <span class="t-tagline-caption" style="flex: 1">{{{{f.value}}}}</span>
          </div>
        </sc-for>
      </div>
      <div class="t-header-caption" style="height: 32px; display: flex; gap: var(--gap-2x-small-4); align-items: center; justify-content: center; color: var(--text-tertiary)">Xem thêm {icon('Chevrondown-fill', 20, 'var(--icon-tertiary)')}</div>
    </section>
  </main>
{TOAST.format(bottom=98, toast_top=650)}  <nav style="flex: none; background: var(--background-primary); box-shadow: 0 4px 8px rgba(34,34,34,.12)">
    <div style="display: flex; gap: var(--gap-2x-small-4); align-items: center; padding: var(--padding-x-small-8) var(--padding-medium-16)">
      <button class="t-label-page h-neutral" style="flex: 1; min-width: 0; height: 40px; border: 0; border-radius: var(--radius-card-small); background: var(--background-secondary); color: var(--text-primary)">Zalo</button>
      <button class="t-label-page h-neutral" onClick="{{{{onChat}}}}" style="flex: 1; min-width: 0; height: 40px; border: 0; border-radius: var(--radius-card-small); background: var(--background-secondary); color: var(--text-primary)">Chat</button>
      <button class="t-label-page h-brand" style="flex: 1; min-width: 0; height: 40px; border: 0; border-radius: var(--radius-card-small); display: inline-flex; align-items: center; justify-content: center; gap: var(--gap-x-small-8); background: var(--button-primary); color: var(--text-on-background)">{icon('Phonecall-outline', 24)}Gọi</button>
    </div>
    {home}
  </nav>
  <sc-if value="{{{{hot}}}}" hint-placeholder-val="{{{{false}}}}">
    <div aria-hidden="true" style="position: absolute; left: 128px; top: 726px; width: 119px; height: 48px; box-sizing: border-box; border: 2px solid var(--border-active); pointer-events: none"></div>
  </sc-if>
</div>
</x-dc>
''' + SCRIPT.format(
    defaults=json.dumps(dict(title='Căn hộ Vinhomes Central Park 3PN 2WC 80M2 gần Landmark 81', params=['3 PN', 'Hướng Đông Nam', 'Chung cư'], price='3,25 tỷ',
                             unitPrice='45,69 tr/m²', area='72 m²', location='Phường 22, Quận Bình Thạnh', project='Vinhomes Central Park', time='23 phút trước',
                             photoCount='1/5', features=[{'label': 'Tình trạng BĐS:', 'value': 'Đã bàn giao'}, {'label': 'Hướng nhà:', 'value': 'Hướng đông nam'},
                                                         {'label': 'Diện tích:', 'value': '72 m²'}, {'label': 'Đơn giá:', 'value': '45,69 tr/m²'}, {'label': 'Số phòng ngủ:', 'value': '3 phòng'}]),
                        ensure_ascii=False),
    extra='', more='')
open(f'{P}/AdViewPTY.dc.html', 'w').write(pty)

# Screen: route ad.layout === 'pty' to AdViewPTY
s = open(f'{P}/Screen.dc.html').read()
old = '''      <dc-import name="AdViewV" ad="{{ad}}" hot="{{hot}}" toast="{{toast}}" on-chat="{{onChat}}" on-view="{{onView}}" hint-size="375px,812px"></dc-import>'''
if 'AdViewPTY' not in s:
    assert old in s
    s = s.replace(old, '''      <sc-if value="{{adMarket}}" hint-placeholder-val="{{true}}">
  ''' + old + '''
      </sc-if>
      <sc-if value="{{adPty}}" hint-placeholder-val="{{false}}">
        <dc-import name="AdViewPTY" ad="{{ad}}" hot="{{hot}}" toast="{{toast}}" on-chat="{{onChat}}" on-view="{{onView}}" hint-size="375px,812px"></dc-import>
      </sc-if>''')
    s = s.replace("      ad: p.ad, adJob: !p.ad, adV: !!p.ad,", "      ad: p.ad, adJob: !p.ad, adV: !!p.ad, adPty: !!p.ad && p.ad.layout === 'pty', adMarket: !!p.ad && p.ad.layout !== 'pty',")
    assert 'adPty:' in s
    open(f'{P}/Screen.dc.html', 'w').write(s)

t = open(f'{P}/vlt-tokens.css').read()
if '--background-warning' not in t:
    t = t.replace('  --background-success: #12a154;', '  --background-success: #12a154;\n  --background-warning: #fb7328;', 1)
    assert '--background-warning' in t
    open(f'{P}/vlt-tokens.css', 'w').write(t)
print('ok')
