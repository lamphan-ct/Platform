"""Generate the Treatment 1 revamp flow (flow, rules, edge cases, prototype) for GDS, VEH and PTY."""
import json
import re
import sys

P = sys.argv[1]  # project dir

V = {
    'GDS': dict(
        name='Chợ Tốt', theme='theme-chotot',
        ad=dict(title='Apple iPhone 14 Pro 128GB Đen Hàn Quốc', subtitle='iPhone 14 Pro • 128 GB', price='12.300.000 đ',
                tags=['Kèm phụ kiện', 'Có đổi trả', 'Có quà tặng'], marketLow='9,91 triệu', marketHigh='12,12 triệu', marketCur='12,30 triệu', curPct=82,
                location='Phường 17, Quận Bình Thạnh, Tp Hồ Chí Minh', location2='Phường Gia Định, TP Hồ Chí Minh mới', time='3 phút trước', photoCount='1/6'),
        q=['Hàng còn không bạn?', 'Còn bảo hành không ạ?', 'Xin thêm hình thực tế ạ', 'Giá còn thương lượng không ạ?', 'Có giao hàng không ạ?'],
        typing='Hàng còn không bạn ơi', short='Mình qua xem máy chiều nay được không?',
        long='Cho mình hỏi máy đã thay pin hay linh kiện gì chưa, có hộp và phụ kiện đầy đủ không bạn',
        source='config Chợ Tốt (back-office)'),
    'VEH': dict(
        name='Chợ Tốt Xe', theme='theme-chotot',
        ad=dict(title='Toyota Vios 1.5G 2020 số tự động, xe gia đình chính chủ', subtitle='Vios • 2020 • 45.000 km', price='435.000.000 đ',
                tags=['Chính chủ', 'Đã kiểm định', 'Hỗ trợ trả góp'], marketLow='410 triệu', marketHigh='455 triệu', marketCur='435 triệu', curPct=55,
                location='Phường Tân Định, Quận 1, Tp Hồ Chí Minh', location2='Phường Tân Định, TP Hồ Chí Minh mới', time='15 phút trước', photoCount='1/8'),
        q=['Xe còn không ạ?', 'Xe chính chủ không ạ?', 'Đã đi bao nhiêu km rồi ạ?', 'Giá còn thương lượng không ạ?', 'Xem xe ở đâu ạ?'],
        typing='Xe còn không anh ơi', short='Cuối tuần mình qua xem xe được không anh?',
        long='Cho mình hỏi xe đã thay những gì, còn đăng kiểm tới khi nào và có hỗ trợ sang tên không anh',
        source='config Chợ Tốt Xe (back-office)'),
    'PTY': dict(
        name='Nhà Tốt', theme='theme-pty',
        ad=dict(layout='pty', title='Căn hộ Vinhomes Central Park 3PN 2WC 80M2 gần Landmark 81', params=['3 PN', 'Hướng Đông Nam', 'Chung cư'], price='3,25 tỷ',
                unitPrice='45,69 tr/m²', area='72 m²', location='Phường 22, Quận Bình Thạnh', project='Vinhomes Central Park', time='23 phút trước', photoCount='1/5'),
        q=['Sổ chung hay riêng z ạ?', 'Có hỗ trợ trả góp ko sốp?', 'Xin video/hình thực tế ạ', 'Xin vị trí cụ thể nhé sốp', 'Giá còn thương lượng không ạ'],
        typing='Hi bạn ơi cho mình hỏi', short='Cuối tuần mình qua xem nhà được không bạn?',
        long='Cho mình hỏi nhà có bị quy hoạch hay tranh chấp gì không, hẻm trước nhà rộng bao nhiêu mét bạn',
        source='bộ câu hỏi Enquiry Form theo ad_type (bán / cho thuê)'),
}
PHONE = 'Gọi lại cho tôi qua SĐT 0987654321'

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
{body}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{props}'>
class Component extends DCLogic {{
  renderVals() {{ return {vals}; }}
}}
</script>
</body>
</html>
'''


def write(name, title, body, vals, w, h):
    props = json.dumps({'$preview': {'width': w, 'height': h}})
    open(f'{P}/{name}.dc.html', 'w').write(HEAD.format(title=title, body=body, props=props, vals=vals))


def js(o):
    return json.dumps(o, ensure_ascii=False)


boards = {}   # file -> (x, y, w, h, title, extra)
static = []   # boards to flatten
order = []


def add(f, x, y, w, h, title, **extra):
    boards[f + '.dc.html'] = dict(x=x, y=y, w=w, h=h, title=title, page='revamp', **extra)
    order.append(f + '.dc.html')


def note(f, w, h, head, items, title):
    lis = ''.join(f'<li>{i}</li>' for i in items)
    body = f'''<div style="width: {w}px; height: {h}px; box-sizing: border-box; overflow: hidden; padding: var(--padding-medium-16); display: flex; flex-direction: column; gap: 10px; background: var(--background-primary); border-radius: var(--radius-card); border-top: 4px solid var(--border-active); font-family: 'Reddit Sans', sans-serif; color: var(--text-primary)">
  <h3 class="t-display-annotation" style="margin: 0">{head}</h3>
  <div style="height: 1px; background: var(--border-thin)"></div>
  <ul class="t-body-section" style="margin: 0; padding-left: 20px; display: flex; flex-direction: column; gap: 4px">{lis}</ul>
</div>'''
    write(f, title, body, '{}', w, h)


section = open(f'{P}/Section-T1.dc.html').read()
pflow = open(f'{P}/Panel-T1-Flow.dc.html').read()
pdf = open(f'{P}/Panel-T1-DefaultForm.dc.html').read()
psend = open(f'{P}/Panel-T1-Send.dc.html').read()
main = open(f'{P}/Main.dc.html').read()

for vi, (k, v) in enumerate(V.items()):
    oy = vi * 2716
    th = v['theme']
    ad = v['ad']
    q = v['q']
    base = dict(variant='r1', thumb='photo', title=ad['title'], price=ad['price'], selected=q[:3], suggest=q[3:])

    def screen(f, title, attrs, cfg=None, msgs=None, w=375):
        vals = {'yes': True, 'ad': ad}
        if cfg is not None:
            vals['cfg'] = cfg
        if msgs is not None:
            vals['msgs'] = msgs
        extra = ' cfg="{{cfg}}"' if cfg is not None else ''
        extra += ' msgs="{{msgs}}"' if msgs is not None else ''
        body = (f'<div class="{th}" style="width: {w}px; height: 812px; overflow: hidden">\n'
                f'<dc-import name="Screen" ad="{{{{ad}}}}" {attrs}{extra} hint-size="{w}px,812px"></dc-import>\n</div>')
        write(f, title, body, js(vals), w, 812)
        static.append(f)

    def sheet(f, title, cfg):
        body = (f'<div class="{th}" style="width: 375px; overflow: hidden; background: var(--background-app)">\n'
                f'<dc-import name="ChatSheetR1" cfg="{{{{cfg}}}}" hint-size="375px,317px"></dc-import>\n</div>')
        write(f, title, body, js({'cfg': dict(base, **cfg)}), 375, 317)
        static.append(f)

    def msg(f, title, m):
        m = dict(tone='yellow', title=ad['title'], price=ad['price'], thumb='photo', **m)
        body = ('<div class="theme-chotot" style="width: 390px; box-sizing: border-box; padding: var(--padding-medium-16); display: flex; justify-content: flex-end; align-items: flex-start; background: var(--background-app)">\n'
                '<dc-import name="Bubble" msg="{{msg}}" hint-size="267px,240px"></dc-import>\n</div>')
        write(f, title, body, js({'msg': m}), 390, 300)
        static.append(f)

    sent = dict(tone='yellow', title=ad['title'], price=ad['price'], thumb='photo', header=True, qs=q[:3], after=[PHONE], text=v['typing'])
    # Section + panels
    s = section.replace('AB group = Treatment 1', f'{v["name"]} ({k}) · Treatment 1').replace(
        'Chọn sẵn 3 câu hỏi + checkbox “Gọi lại cho tôi qua SĐT”', 'Layout sheet mới · chọn sẵn 3 câu hỏi + checkbox “Gọi lại cho tôi qua SĐT”')
    s = re.sub(r'<title>[^<]*</title>', f'<title>{k} · Treatment 1</title>', s, count=1)
    open(f'{P}/Section-{k}.dc.html', 'w').write(s)
    add(f'Section-{k}', 0, oy, 4213, 2516, f'{v["name"]} · Treatment 1', radius=20)
    s = pflow.replace('id="t1a"', f'id="{k.lower()}a"').replace('url(#t1a)', f'url(#{k.lower()}a)')
    s = re.sub(r'<title>[^<]*</title>', f'<title>{k} · Flow chính</title>', s, count=1)
    open(f'{P}/Panel-{k}-Flow.dc.html', 'w').write(s)
    add(f'Panel-{k}-Flow', 80, oy + 172, 4053, 1036, f'{k} · Flow chính', radius=20)
    s = pdf.replace('· note, ô nhập, default form', '· note, default form, chip, SĐT chưa xác thực')
    s = re.sub(r'<title>[^<]*</title>', f'<title>{k} · Quy tắc</title>', s, count=1)
    open(f'{P}/Panel-{k}-Rules.dc.html', 'w').write(s)
    add(f'Panel-{k}-Rules', 80, oy + 1288, 4053, 446, f'{k} · Quy tắc & trạng thái', radius=20)
    s = psend.replace('id="e1a"', f'id="{k.lower()}e"').replace('url(#e1a)', f'url(#{k.lower()}e)')
    s = re.sub(r'<title>[^<]*</title>', f'<title>{k} · Edge cases</title>', s, count=1)
    open(f'{P}/Panel-{k}-Edge.dc.html', 'w').write(s)
    add(f'Panel-{k}-Edge', 80, oy + 1814, 4053, 622, f'{k} · Edge cases', radius=20)

    # Flow
    fy = oy + 272
    screen(f'{k}-01-AdView', f'{k} · Chi tiết tin', 'mode="ad" hot="{{yes}}"')
    add(f'{k}-01-AdView', 120, fy, 375, 812, '1 · Chi tiết tin → tap Chat')
    screen(f'{k}-02-Sheet', f'{k} · Sheet mặc định', 'mode="sheet"', cfg=base)
    add(f'{k}-02-Sheet', 575, fy, 375, 812, '2 · Sheet mặc định')
    screen(f'{k}-03-Focus', f'{k} · Focus ô nhập', 'mode="sheet" kb="{{yes}}"', cfg=dict(base, placeholder='|Nhập tin nhắn…'))
    add(f'{k}-03-Focus', 1030, fy, 375, 812, '3 · Focus ô nhập')
    screen(f'{k}-04-Typing', f'{k} · Đang nhập', 'mode="sheet" kb="{{yes}}"', cfg=dict(base, text=v['typing'] + '|'))
    add(f'{k}-04-Typing', 1485, fy, 375, 812, '4 · Đang nhập')
    screen(f'{k}-05-Sent', f'{k} · Gửi thành công', 'mode="ad" toast="{{yes}}"')
    add(f'{k}-05-Sent', 1940, fy, 375, 812, '5 · Gửi thành công')
    screen(f'{k}-06-ChatRoom', f'{k} · Phòng chat', 'mode="chat"', msgs=[sent], w=390)
    add(f'{k}-06-ChatRoom', 2395, fy, 390, 812, '6 · Phòng chat (theme Chợ Tốt)', radius=20)

    # Prototype
    s = main.replace("variant: 't1'", "variant: 'r1', thumb: 'photo', title: AD.title, price: AD.price")
    s = re.sub(r"const Q = \[[^\]]*\];", 'const Q = ' + js(q) + ';\n    const AD = ' + js(ad) + ';', s, count=1)
    s = s.replace("const msg = { header: s.sel.length > 0, qs: s.sel.slice(), after: s.callback && hasPhone ? ['Gọi lại cho tôi qua SĐT 0987654321'] : [], text: s.text.trim() };",
                  "const msg = { tone: 'yellow', title: AD.title, price: AD.price, thumb: 'photo', header: s.sel.length > 0, qs: s.sel.slice(), after: s.callback && hasPhone ? ['Gọi lại cho tôi qua SĐT 0987654321'] : [], text: s.text.trim() };")
    s = s.replace('<dc-import name="Screen" mode', '<dc-import name="Screen" ad="{{ad}}" mode')
    s = s.replace('      mode: s.mode, kb: s.kb,', '      ad: AD, mode: s.mode, kb: s.kb,')
    s = s.replace('<div style="width: 375px; height: 812px; overflow: hidden;', f'<div class="{th}" style="width: 375px; height: 812px; overflow: hidden;', 1)
    s = re.sub(r'<title>[^<]*</title>', f'<title>Prototype {k} · Treatment 1</title>', s, count=1)
    for must in ["tone: 'yellow'", 'ad="{{ad}}"', 'ad: AD', f'class="{th}"', 'const AD']:
        assert must in s, (k, must)
    open(f'{P}/{k}-Prototype.dc.html', 'w').write(s)
    add(f'{k}-Prototype', 2905, fy, 375, 812, f'▶ Prototype · {v["name"]}', is_interactive=True, radius=40)

    # Rules row
    ry = oy + 1388
    main_items = [f'Chọn sẵn 3 câu đầu theo {v["source"]}. Ít hơn 3 câu → chọn hết; rỗng/lỗi → không có chip',
                  'Checkbox “Gọi lại cho tôi qua SĐT…” chỉ hiện khi SĐT đã xác thực, mặc định checked']
    if k == 'PTY':
        main_items += ['<b>SĐT chưa xác thực → ẩn checkbox, vẫn gửi được</b> (PTY bản đầu chỉ mở cho user đã xác thực — PM xác nhận)']
    else:
        main_items += ['<b>SĐT chưa xác thực → ẩn checkbox, vẫn gửi được, không nhắc xác thực</b>']
    main_items += ['Vượt chat limit → không mở sheet, toast “Bạn cần xác thực số điện thoại”']
    note(f'{k}-Note-Main', 296, 312, 'Note <span style="color: var(--text-error)">(*)</span>', main_items, f'{k} · Note')
    static.append(f'{k}-Note-Main')
    add(f'{k}-Note-Main', 120, ry, 296, 312, 'Note', radius=12)
    sheet(f'{k}-DF-Sheet1', f'{k} · Default form', {})
    add(f'{k}-DF-Sheet1', 456, ry, 375, 317, 'Default form')
    note(f'{k}-Note-DF1', 375, 152, 'Bỏ câu hỏi', ['Chip bị bỏ quay về list “Hỏi thêm” <b>đúng vị trí theo thứ tự config</b>', 'Bỏ hết câu đã chọn → ẩn “Cho mình hỏi:”'], f'{k} · Note bỏ câu hỏi')
    static.append(f'{k}-Note-DF1')
    add(f'{k}-Note-DF1', 871, ry, 375, 152, 'Note · Remove question', radius=12)
    sheet(f'{k}-DF-Sheet2', f'{k} · Chọn hết gợi ý', {'selected': q, 'suggest': []})
    add(f'{k}-DF-Sheet2', 1286, ry, 375, 317, 'Default form · chọn hết gợi ý')
    note(f'{k}-Note-DF2', 375, 152, 'Chọn câu ở “Hỏi thêm”', ['Câu được chọn thêm vào cuối “Cho mình hỏi:”', 'Chọn hết câu trong list → ẩn list “Hỏi thêm”', 'Câu đã chọn: mỗi hàng 2 chip, dài hơn khung → scroll ngang'], f'{k} · Note chọn câu')
    static.append(f'{k}-Note-DF2')
    add(f'{k}-Note-DF2', 1701, ry, 375, 152, 'Note · Chọn câu hỏi', radius=12)
    sheet(f'{k}-DF-Rows', f'{k} · 4 câu, 2 chip mỗi hàng', {'selected': q[:4], 'suggest': q[4:]})
    add(f'{k}-DF-Rows', 2116, ry, 375, 317, 'Chọn 4 câu · 2 chip/hàng')
    sheet(f'{k}-DF-NoPhone', f'{k} · SĐT chưa xác thực', {'showCb': False})
    add(f'{k}-DF-NoPhone', 2531, ry, 375, 291, 'SĐT chưa xác thực → ẩn checkbox')

    # Edge cases
    ny, sy = oy + 1914, oy + 2042
    cases = [
        ('C1', 'In case: xoá hết câu hỏi và chưa nhập', ['Nút Gửi disabled, tap không có action'], 375,
         {'selected': [], 'suggest': q}, None),
        ('C2', 'In case: câu hỏi + text', ['Text dài → hiện tối đa 2 dòng rồi scroll trong ô nhập', 'Tin gửi: bullet câu hỏi → text → dòng SĐT ở cuối'], 852,
         {'text': v['long']}, dict(header=True, qs=q[:3], text=v['long'], after=[PHONE])),
        ('C3', 'In case: chỉ câu hỏi', ['Tin gửi: “Cho mình hỏi:” + bullet câu hỏi → dòng SĐT'], 852,
         {}, dict(header=True, markHeader=True, qs=q[:3], after=[PHONE])),
        ('C4', 'In case: chỉ text', ['Bỏ hết câu hỏi, chỉ nhập text → tin gửi: text → dòng SĐT'], 852,
         {'selected': [], 'suggest': q, 'text': v['short']}, dict(header=False, qs=[], text=v['short'], after=[PHONE])),
        ('C5', 'In case: bỏ tick “Gọi lại cho tôi qua SĐT…”', ['Tin gửi không kèm dòng SĐT'], 882,
         {'callback': False}, dict(header=True, qs=q[:3], after=[])),
    ]
    xs = [(120, None), (535, 950), (1427, 1842), (2319, 2734), (3211, 3626)]
    for (c, head, items, nw, cfg, m), (sx, mx) in zip(cases, xs):
        note(f'{k}-Note-{c}', nw, 104, head, items, f'{k} · {c}')
        static.append(f'{k}-Note-{c}')
        add(f'{k}-Note-{c}', sx, ny, nw, 104, f'Case {c[1]}', radius=12)
        sheet(f'{k}-{c}-Sheet', f'{k} · {c} sheet', cfg)
        add(f'{k}-{c}-Sheet', sx, sy, 375, 317, 'Sheet')
        if m:
            msg(f'{k}-{c}-Msg', f'{k} · {c} tin đã gửi', m)
            add(f'{k}-{c}-Msg', mx, sy, 390, 300, 'Tin đã gửi')

json.dump({'boards': boards, 'order': order, 'static': static}, open(f'{P}/../gen-out.json', 'w'), ensure_ascii=False, indent=1)
print(len(boards), 'boards,', len(static), 'static')
