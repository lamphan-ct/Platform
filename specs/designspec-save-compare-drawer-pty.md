# Design Spec — Compare suggestion drawer after saving a PTY ad (Mobile)

**Story:** STORY-004 · PRD: Save hub Re-design (Confluence 4969758867) · Ticket: PLMO-3204
**Vertical:** PTY (Nhà Tốt) · **Platform:** App (iOS / Android)
**Design owner:** Lâm Phan · **Spec version:** v2 · **Date:** 2026-10-15
**Source HTML:** Design canvas “Nhà Tốt AdView” → page “Lưu → So sánh”
- Static flow + edge cases: `CompareFlow.dc.html` (+ `screens.css`)
- Interactive prototype: `Compare1Tap.dc.html` (AdView + drawer + compare)
- Spec-ready: CHOTOT DS v3.0 tokens only, `data-ds-*` on every handoff element, `ds_lint` clean. AdView = `data-ds-context="reference"` (host screen, not handed off).

**Figma:** reference only — PRD + design spec thắng khi lệch.
**Loading:** không có loading cho drawer (PRD: chờ tối đa 1s, không spinner/skeleton) — xem §Display Condition.

> **Changes v1 → v2 (design owner, 2026-10-13 → 15)**
> 1. Trigger theo PRD mới: API gợi ý gọi song song API lưu, **chờ tối đa 1s**, không loading; không có data → toast hiện tại. Bỏ trạng thái skeleton.
> 2. Header: **“Lưu thành công”** + link **“Đến trang Đã lưu”** (gạch chân, text-primary). Không nút X, **không nút “Đóng”** — CTA full width.
> 3. Danh sách gợi ý là **1 list chung** dưới tiêu đề **“Chọn thêm tin tương tự để so sánh”** + dòng filter. Không còn tiêu đề theo nhóm; tim đỏ trên ảnh = tin đã lưu.
> 4. Mọi ad card dùng chung bố cục với tin vừa lưu; dòng cuối = **vị trí** (bỏ “Đã lưu · 3 ngày trước”).
> 5. Drawer cao **70%** màn, cuộn list → giãn lên **90%**.
> 6. SnackBar theo component DS (action màu `text-chotot`). Checkbox theo DS `checkbox.md`. Icon = DS sprite.

---

## Open Items

```yaml
checkpoints:
  - id: CP-07
    blocking: false
    topic: Frequency cap
    detail: PRD không giới hạn số lần mở drawer. Có cần cap (vd N lần/ngày, sau đó dùng toast)?
  - id: CP-08
    blocking: false
    topic: Tin của chính user
    detail: Loại tin do chính user đăng khỏi danh sách gợi ý? Đề xuất loại (PRD chưa nêu).
  - id: CP-10
    blocking: false
    topic: Copy toast fallback
    detail: PRD “show the existing toast unchanged”. Prototype minh hoạ “Đã lưu tin · Đến trang Đã lưu”; production đang là “Lưu thành công! · Đến trang Đã lưu” → dev giữ đúng copy production.
  - id: CP-11
    blocking: false
    topic: DS chưa có (nhóm B)
    detail: Grabber, header không nút X (icon + title + link), Tag “Rẻ nhất”, nút ✕ nền tối trên ảnh, link màu text-primary. Đã gắn data-ds-raw — DS owner chốt có đưa vào DS không.
  - id: CP-12
    blocking: false
    topic: PRD cần cập nhật
    detail: (a) Màn So sánh ẩn nút ✕ khi chỉ còn 2 tin (PRD STORY-002 ghi mọi tin có ✕). (b) Drawer 70% → 90% khi cuộn, dòng filter dưới tiêu đề — chưa có trong PRD.
```

---

## Overview

Khi user **đã đăng nhập** lưu một tin **PTY** và API gợi ý trả **≥ 1 tin** trong vòng **1s**, app mở **drawer gợi ý so sánh** thay cho toast lưu tin. User chọn **2–4 tin** (gồm tin vừa lưu) rồi mở **màn So sánh hiện có (STORY-002)**.

Happy path: AdView → tap Lưu → drawer mở (tin vừa lưu chọn sẵn) → chọn thêm 1–3 tin → tap “So sánh (n/4)” → màn So sánh.

| # | Screen | Scope |
|---|---|---|
| 1 | AdView PTY + nút Lưu | Host — reference, chỉ đổi phản hồi sau khi lưu |
| 2 | Compare suggestion drawer | **Mới** — spec chính |
| 3 | Comparison result | Dùng lại STORY-002 — chỉ ghi phần liên quan |

---

## Display Condition

| Điều kiện | Kết quả |
|---|---|
| Tap Lưu | Gọi **Save API** và **Recommended-ads API song song**; timer 1s bắt đầu từ lúc tap. Icon tim đổi sang đã lưu như hiện tại; **không** spinner/skeleton |
| Save OK **và** API trả ≥ 1 tin trong ≤ 1s | Mở drawer (thay toast) |
| API trả 0 tin / lỗi / không phản hồi trong 1s | Toast lưu tin hiện tại, không đổi (CP-10) |
| API phản hồi sau 1s | Bỏ kết quả, **không bao giờ** mở drawer |
| Save lỗi | Xử lý lỗi hiện tại, không drawer |
| Chưa đăng nhập | Flow login hiện tại |
| Bỏ lưu | Không drawer — SnackBar “Đã bỏ lưu.” + “Đến trang Đã lưu” |
| Vertical khác PTY | Không áp dụng |

**Tin gợi ý (PRD)** — khớp cả 4 điều kiện với tin vừa lưu: loại tin (bán/thuê), danh mục, cùng tỉnh/thành **và** quận/huyện, giá trong **±20%**. Loại trừ: chính tin vừa lưu, tin không còn active (ẩn, hết hạn, gỡ).

## Display Position

- Bottom sheet trên AdView, scrim phủ toàn màn.
- Mở ở **70%** chiều cao màn. Khi user cuộn list (scrollTop > 8pt) → sheet giãn lên **90%** (300ms), giữ 90% tới khi đóng. Mỗi lần mở lại bắt đầu từ 70%.
- Header + footer cố định, body cuộn.

---

## Interaction Rules

| Element | Trigger | Behavior |
|---|---|---|
| Nút Lưu | Tap khi chưa lưu | Theo §Display Condition; chặn tap lặp tới khi có kết quả |
| Nút Đã lưu | Tap | Bỏ lưu → SnackBar “Đã bỏ lưu.” + action “Đến trang Đã lưu” |
| Link “Đến trang Đã lưu” | Tap | Đóng drawer → Hoạt động › tab **Đã lưu** (`chotot-app://www.chotot.com/activity/da-luu`) |
| Ad card | Tap **bất kỳ điểm nào** trên card | Toggle chọn/bỏ chọn. **Không** mở AdView |
| Ad card khi đã chọn 4 | Tap card chưa chọn | Không đổi trạng thái, không animation → SnackBar “Chỉ được chọn tối đa 4 tin để so sánh” |
| List | Cuộn | Sheet 70% → 90% (một chiều) |
| Scrim | Tap | Đóng drawer |
| Sheet | Vuốt xuống | Đóng drawer |
| Back (Android) | Press | Đóng drawer |
| CTA “So sánh (n/4)” | Tap khi 2 ≤ n ≤ 4 | Mở màn So sánh (STORY-002) với các tin đã chọn, theo thứ tự trong drawer |
| Màn So sánh › Back | Tap | Về drawer, giữ nguyên lựa chọn |
| Màn So sánh › ✕ | Tap | Bỏ tin khỏi bảng; **chỉ hiện khi > 2 tin** (CP-12a) |

## Common Rules

- Tin vừa lưu luôn **đầu danh sách**, **chọn sẵn**, bỏ chọn được.
- n = tổng tin đang chọn (gồm tin vừa lưu). CTA enabled khi **2 ≤ n ≤ 4**.
- Thứ tự gợi ý (1 list chung, không tiêu đề nhóm):
  1. **Đã lưu → đã xem → tin khác trên Nhà Tốt**. Vừa lưu vừa xem → tính là đã lưu.
  2. Trong nhóm: chênh lệch giá tuyệt đối với tin vừa lưu **tăng dần**; bằng nhau → tin đăng **mới hơn** trước.
  3. Tối đa **10** tin gợi ý (không tính tin vừa lưu), cuộn trong drawer.
- Tim trên ảnh: **Heart-fill** (icon-error) = đã lưu · **Heart-outline** (icon-blank) = chưa lưu.
- Màn So sánh: tag “Rẻ nhất” theo logic STORY-002 (tính một lần khi bảng load, bỏ tin không tính lại). Header = tên nhóm tính theo STORY-002.

---

## Layout YAML

```yaml
screen: compare-suggestion-drawer
platform: app
container:
  type: Drawer                                   # source: section.sheet[data-ds=Drawer]
  scrim: background-overlay (rgba(34,34,34,0.50))
  sheet:
    background: background-primary (#FFFFFF)
    radius-top: radius-modal (20)
    shadow: shadow-floating (0 4 16 rgba(34,34,34,0.12))
    height: 70% → 90% on scroll                  # data-ds-raw: product rule
    grabber: { width: 36, height: 4, radius: radius-pill, color: border-regular (#DDDDDD), margin-top: spacing-8 }   # data-ds-raw: DS chưa có
  children:
    - header:                                    # source: .sh-head
        layout: row, align-center, gap: spacing-8
        padding: spacing-16 spacing-16 spacing-12
        children:
          - Icon: { props: { name: CircleCheck-fill, size: 24 }, color: icon-success (#12A154) }
          - text: { value: "Lưu thành công", typo: display-annotation (18/26/700), color: text-primary (#222222), flex: 1 }
          - link: { value: "Đến trang Đã lưu", typo: header-caption (14/20/600), color: text-primary (#222222), decoration: underline, min-height: 48 }   # data-ds-raw: DS link = text-link
    - body:                                      # source: .sh-body — scroll vertical
        children:
          - ad-card: just-saved                  # chọn sẵn
          - list-header:                         # source: .pk-head.main
              padding: spacing-20 spacing-16 spacing-4
              border-top: 1px border-thin (#E8E8E8)   # = divider của card phía trên
              - title:   { value: "Chọn thêm tin tương tự để so sánh", typo: header-section (16/24/600), color: text-primary (#222222) }
              - filters: { value: "{Loại BĐS} · {Mua bán|Cho thuê} · {Quận}, {Tỉnh} · {giá−20%}–{giá+20%}", typo: body-caption (12/18/400), color: text-secondary (#595959), margin-top: spacing-2 }
          - ad-card[]: recommended (≤ 10)
    - footer:                                    # source: .sh-foot
        border-top: 1px border-thin (#E8E8E8)
        padding: spacing-12 spacing-16 0
        actions:
          - Button: { props: { type: Primary, size: L-40, pill: false, label: "So sánh (n/4)", disabled: "n < 2" }, width: fill }

ad-card:                                         # source: .pk-item[data-ds="Ad pick card"] — composite
  composite: Thumbnail 100 + Icon Heart 20 + text stack + Checkbox 24
  layout: row, align-start, gap: spacing-12
  padding: spacing-12 spacing-16
  background: background-primary (#FFFFFF)
  divider-bottom: 1px border-thin (#E8E8E8)
  hit-area: toàn card → toggle
  children:
    - thumbnail:
        size: 100x100
        radius: radius-card-small (8)
        fit: cover
        placeholder: background-tertiary (#E8E8E8)
        overlay: { Icon: Heart-fill (icon-error #F0325E) | Heart-outline (icon-blank #FFFFFF), size: 20, top: 4, right: 4 }
    - info:
        layout: column, gap: spacing-4, flex: 1
        children:
          - title:  { typo: tagline-caption (14/20/500), color: text-primary (#222222), max-lines: 2, overflow: ellipsis }
          - params: { typo: body-caption (12/18/400), color: text-secondary (#595959), max-lines: 1, format: "{rooms} PN · Hướng {direction} · {type}" }
          - price-row:
              layout: row, align-baseline, gap: spacing-8
              - price: { value: "{size}m² - {price}", typo: header-section (16/24/600), color: text-error (#F0325E) }
              - ppm:   { value: "{price_m2} tr/m²", typo: tagline-annotation (12/18/500), color: text-primary (#222222) }
          - location: { value: "{district} ({ward})", typo: body-caption (12/18/400), color: text-secondary (#595959), max-lines: 1 }
    - Checkbox:
        props: { type: Standard, size: 24, state: Default }
        align-self: start
```

## DS Components Used

| Component | Variant / props | Ghi chú |
|---|---|---|
| Drawer | Mobile, radius-modal top, shadow-floating | Tuỳ chỉnh: không nút X, header thành công, grabber (CP-11) |
| Checkbox | Standard 24 (ô 20, radius-ad-small, viền 2px) | Checked = background-brand PTY + Check-outline 16 icon-blank |
| Button | Primary · L-40 · not pill | “So sánh (n/4)”, label-page 16/24 Bold |
| SnackBar | App · action · no icon | Theo component DS |
| Icon | CircleCheck-fill · Heart-fill · Heart-outline · Check-outline · Arrowleft-outline · Close-outline | DS sprite |
| Icon Button | XL-48 Ghost (back) · S-24 custom (✕ trên ảnh) | Màn So sánh |

## Design Tokens Map

| Usage | Token | Value |
|---|---|---|
| Scrim | background-overlay | rgba(34,34,34,0.50) |
| Sheet, card bg | background-primary | #FFFFFF |
| Thumbnail placeholder | background-tertiary | #E8E8E8 |
| Title, ppm, header text, link | text-primary | #222222 |
| Params, location, filter line | text-secondary | #595959 |
| Price | text-error | #F0325E |
| Header success icon | icon-success | #12A154 |
| Heart saved / unsaved | icon-error / icon-blank | #F0325E / #FFFFFF |
| Dividers | border-thin | #E8E8E8 |
| Grabber, checkbox unchecked border | border-regular | #DDDDDD |
| Checkbox hover border | border-black | #222222 |
| Primary bg / checkbox checked (PTY) | background-brand | #FA6819 |
| Primary label, checkbox tick | text-on-background / icon-blank | #FFFFFF |
| Primary hover / pressed | interaction-brand-hover / -pressed | #FB8F4A / #E05A10 |
| Primary disabled | button-disabled + text-blank | #C0C0C0 / #FFFFFF |
| SnackBar bg | background-inverted @ 90% | #222222 |
| SnackBar message / action | text-blank / text-chotot | #FFFFFF / #FFD400 |
| Shadow | shadow-floating | 0 4 16 rgba(34,34,34,0.12) |

### Non-tokenizable values
| Value | Where | Reason |
|---|---|---|
| 70% / 90% height | Drawer | product rule |
| Grabber 36×4 | Drawer | DS chưa có |
| SnackBar opacity 90% | SnackBar | theo code DS SnackBar |

## Assets

Không có asset mới. Thumbnail = ảnh tin (user content). Icon = DS sprite (đã liệt kê ở §DS Components).

---

## Interaction States

### Checkbox (DS checkbox.md — Standard)
| State | Spec |
|---|---|
| Unchecked | Ô 20 (inset 2), viền 2px border-regular #DDDDDD, bg #FFFFFF |
| Hover (card hover) | Viền border-black #222222 |
| Checked | Bg + viền background-brand #FA6819, Check-outline 16 icon-blank #FFFFFF |
| Focus | Outline 2px border-black, offset 2 |

### Button “So sánh (n/4)” — Primary L-40 PTY
| State | Bg | Label |
|---|---|---|
| Default | background-brand #FA6819 | text-on-background #FFFFFF |
| Hover | interaction-brand-hover #FB8F4A | #FFFFFF |
| Pressed | interaction-brand-pressed #E05A10 | #FFFFFF |
| Disabled (n < 2) | button-disabled #C0C0C0 | text-blank #FFFFFF |

## Content Rules

| Field | Rule |
|---|---|
| Title | Tối đa 2 dòng, ellipsis |
| Params | 1 dòng; thiếu trường thì bỏ trường + dấu “·” liền kề |
| Price | `{size}m² - {price}`, format giá hiện tại (tỷ / triệu) |
| Price/m² | `{x} tr/m²`, tối đa 2 chữ số thập phân, dấu phẩy |
| Location | `{district} ({ward})`, 1 dòng, ellipsis — áp cho mọi card |
| Filter line | `{Loại BĐS} · {Mua bán\|Cho thuê} · {Quận}, {Tỉnh} · {giá×0.8}–{giá×1.2}` theo format giá hiện tại (vd giá 3,25 tỷ → “2,6–3,9 tỷ”) |
| CTA | “So sánh (n/4)” |

### SnackBar (DS · App · action · no icon)
Full width, margin-x 16, nằm trên footer/bottom bar. bg background-inverted 90%, radius-card (12), padding spacing-12 × spacing-16, gap spacing-8. Message body-section (14/20/400) text-blank; action label-section (14/20/700) **text-chotot #FFD400**, căn phải, không gạch chân.

| Case | Copy | Action | Duration |
|---|---|---|---|
| Chọn tin thứ 5 | Chỉ được chọn tối đa 4 tin để so sánh | — | 3s |
| Bỏ lưu | Đã bỏ lưu. | Đến trang Đã lưu | 3s |
| Fallback (không drawer) | Toast production hiện tại (CP-10) | Đến trang Đã lưu | như hiện tại |

## Edge Cases

| Case | Behavior |
|---|---|
| API gợi ý trả 0 tin / lỗi / > 1s | Không drawer → toast hiện tại |
| Chỉ có tin “khác trên Nhà Tốt” (chưa lưu/xem tin nào) | Vẫn 1 list, cùng tiêu đề + filter |
| > 10 tin gợi ý | Cắt còn 10 theo thứ tự §Common Rules |
| Bỏ chọn tin vừa lưu | Cho phép; CTA disabled nếu n < 2 |
| Đạt 4 tin | Card khác hiển thị bình thường; tap → SnackBar giới hạn |
| Tap Lưu liên tục | Chỉ gọi API & mở drawer 1 lần |
| Tin trong list bị ẩn trong lúc drawer mở | Không xử lý realtime — STORY-002 xử lý ở màn So sánh |
| Chưa login / lưu lỗi | Flow hiện tại |

---

## Tagging & Analytics (PRD)

| Event | When |
|---|---|
| `save_ad_compare_drawer_show` | Drawer hiển thị |
| `save_ad_compare_picker_submit` | Tap “So sánh (n/4)” |
| `screen_view_saved_activity` | Mở trang Đã lưu từ link “Đến trang Đã lưu” |

Màn So sánh dùng lại event STORY-002 (`screen_view_compare_result`, `save_ad_compare_result_*`). Param do PM/Data chốt theo tagging plan.

---

## Prototype Quality

| Hạng mục | Đánh giá |
|---|---|
| Naming / structure | ✅ class có nghĩa, DOM ≤ 5 tầng/cụm |
| Token binding | ✅ 100% `var(--token)`; `ds_lint` sạch; raw có `data-ds-raw` |
| `data-ds-*` | ✅ Drawer, Button, Checkbox, SnackBar, Ad card (composite), Icon Button, typo/color |
| Icons | ✅ DS sprite |
| Interaction coverage | ✅ Happy path, giới hạn 4, đóng, giãn 90%, snackbar |
| Figma | Cũ — bỏ qua |

**Quality Score:** 93 / 100 — ✅ READY (Intent 38/40 · Edge 27/30 · Interview 19/20 · Prototype 9/10)

## Animations (overrides default)

`spring = cubic-bezier(.34, 1.56, .64, 1)`

| Event | Spec |
|---|---|
| Drawer open | translateY 100% → 0, 300ms `(.2,.8,.2,1)`; scrim 0 → 1, 200ms ease |
| Drawer close | translateY 0 → 100%, 250ms `(.4,0,1,1)`; scrim 1 → 0, 250ms ease; khoá input khi đang đóng |
| Expand 70% → 90% | height 300ms `(.2,.8,.2,1)` |
| checkbox.enter | Mở drawer: scale 0.4 → 1, 320ms spring, stagger 25ms/item |
| checkbox.color | bg + viền 160ms ease |
| checkbox.pop | Khi chọn: 1 → 1.12 (320ms spring), giữ 150ms, → 1 (320ms spring) |
| card.press | Khi chọn: 1 → 0.985 → 1, mỗi chiều 260ms spring |
| cta.bump | Mỗi lần n đổi: 1 → 1.04 → 1, mỗi chiều 260ms spring |
| Over limit | Không animation |
| SnackBar | opacity + translateY 12 → 0, 200ms ease-in-out |
| Reduce Motion | Tắt toàn bộ, state vẫn đổi đúng |

| Curve | iOS | Android (View) | Compose |
|---|---|---|---|
| spring `(.34,1.56,.64,1)` | `CAMediaTimingFunction(controlPoints: 0.34, 1.56, 0.64, 1)` | `PathInterpolator(0.34f, 1.56f, 0.64f, 1f)` | `CubicBezierEasing(0.34f, 1.56f, 0.64f, 1f)` |
| open `(.2,.8,.2,1)` | `CAMediaTimingFunction(controlPoints: 0.2, 0.8, 0.2, 1)` | `PathInterpolator(0.2f, 0.8f, 0.2f, 1f)` | `CubicBezierEasing(0.2f, 0.8f, 0.2f, 1f)` |
| close `(.4,0,1,1)` | `CAMediaTimingFunction(controlPoints: 0.4, 0, 1, 1)` | `PathInterpolator(0.4f, 0f, 1f, 1f)` | `CubicBezierEasing(0.4f, 0f, 1f, 1f)` |
| ease | `.curveEaseInOut` | `AccelerateDecelerateInterpolator` | `FastOutSlowInEasing` |

Motion reference: board Prototype trên canvas.

## Accessibility

- Ad card = 1 control role checkbox, label = title + giá + vị trí; state checked/unchecked.
- Chạm tin thứ 5: announce nội dung SnackBar.
- Tap target ≥ 48pt (card, CTA, link).
- Drawer mở: focus vào “Lưu thành công”; đóng → focus về nút Lưu.

## Known DS Gotchas

- PTY primary là **cam #FA6819 chữ trắng**; checkbox checked cùng màu brand, tick trắng.
- Disabled Primary = button-disabled + chữ trắng, không giảm opacity.
- SnackBar action dùng **text-chotot (vàng)** kể cả ở PTY — theo component DS.
- Drawer không nút X, không nút Đóng.

## Verify Checklist

- [ ] Tap Lưu: API gợi ý song song, không loading; ≥ 1 tin trong 1s → drawer; còn lại → toast; về sau 1s → bỏ.
- [ ] Header “Lưu thành công” + “Đến trang Đã lưu” mở tab Đã lưu.
- [ ] Tin vừa lưu đầu list, chọn sẵn, bỏ chọn được.
- [ ] 1 list dưới “Chọn thêm tin tương tự để so sánh” + filter đúng format; thứ tự đã lưu → đã xem → khác, theo chênh lệch giá; tối đa 10.
- [ ] Mọi card cùng bố cục, dòng cuối = vị trí; tim đúng trạng thái.
- [ ] Chạm bất kỳ đâu trên card đều toggle.
- [ ] CTA full width, disabled khi n < 2; mở màn So sánh; Back giữ lựa chọn.
- [ ] Đạt 4 tin: tap → SnackBar giới hạn, không animation.
- [ ] Drawer 70% → 90% khi cuộn; đóng bằng scrim / vuốt / Back.
- [ ] SnackBar đúng component DS (bo 12, 90%, action text-chotot).
- [ ] Motion đúng token; Reduce Motion tắt animation.
