# Design Spec — Compare suggestion drawer after saving a PTY ad (Mobile)

**Story:** STORY-004 · PRD: Save hub Re-design · Ticket: PLMO-3204
**Vertical:** PTY (Nhà Tốt) · **Platform:** App (iOS / Android)
**Design owner:** Lâm Phan · **Spec version:** v1 · **Date:** 2026-10-12
**Source HTML:** Design canvas “Nhà Tốt AdView” → page “Lưu → So sánh”
- Prototype (interactive): `Compare1Tap.dc.html` → mounts `Main.dc.html` (AdView + drawer + compare)
- Static flow + edge cases: `CompareFlow.dc.html`
- Shared static styles: `screens.css`

**Figma:** reference only — PRD + design spec thắng khi lệch.
**Loading:** DS platform default — decided by design owner.

> **Decisions vs PRD (design owner, 2026-10-12)** — PRD cần cập nhật theo các điểm này:
> 1. Header: **không có nút X**; đóng bằng nút **“Đóng”**, chạm vùng tối, vuốt xuống, Back (Android). Link đổi thành **“Xem tất cả”** (gạch chân, text-primary).
> 2. **Bỏ tag “Tin vừa lưu”** — tin vừa lưu chỉ nằm đầu danh sách, chọn sẵn.
> 3. Danh sách gợi ý chia **3 section có tiêu đề** (đã lưu → đã xem → tin khác trên Nhà Tốt), mỗi tin có **dòng nguồn + thời gian**.
> 4. Đạt 4 tin: tin còn lại **không bị disable**; chạm → snackbar giới hạn.
> 5. CTA label **“So sánh (n/4)”**.

---

## Open Items

```yaml
checkpoints:
  - id: CP-01
    blocking: false
    topic: Section header typography
    detail: Prototype dùng 17/24 Medium (#595959) — không có trong DS scale.
    proposal: body-page (16/24/400) + text-secondary
  - id: CP-02
    blocking: false
    topic: Price-per-m² typography
    detail: Prototype dùng 13/20 Medium — không có trong DS scale.
    proposal: tagline-annotation (12/18/500) hoặc tagline-caption (14/20/500)
  - id: CP-03
    blocking: false
    topic: Spacing ngoài token
    detail: header gap 10, info-stack gap 3, footer padding-top 10.
    proposal: spacing-8 / spacing-4 / spacing-12
  - id: CP-04
    blocking: true
    topic: Icon DS names
    detail: "[ICON: confirm DS name] cho: success circle (header), heart-fill / heart-outline (nguồn trên thumbnail), checkbox tick."
  - id: CP-05
    blocking: false
    topic: Checkbox override
    detail: Spec checkbox 24×24 radius 6, off-border #C0C0C0 (designer). DS Checkbox mặc định 20×20 radius 4.
    proposal: Dùng DS Checkbox, override size/radius; xác nhận với DS team.
  - id: CP-06
    blocking: false
    topic: Time format ở dòng nguồn
    detail: "Đã lưu · 3 ngày trước", "Đã xem · 2 giờ trước", "Đã xem · Hôm qua" — cần chốt bậc thời gian (phút/giờ/hôm qua/ngày/tuần/tháng).
  - id: CP-07
    blocking: false
    topic: Frequency cap
    detail: Có giới hạn số lần mở drawer / ngày không? Sau ngưỡng dùng toast?
  - id: CP-08
    blocking: false
    topic: Tin của chính user
    detail: Loại tin do chính user đăng khỏi danh sách gợi ý? (đề xuất: loại)
  - id: CP-09
    blocking: false
    topic: Tracking
    detail: PRD STORY-004 chưa có event. Đề xuất ở §Tagging — PM/Data chốt tên.
```

---

## Overview

Khi user **đã đăng nhập** lưu thành công một tin **PTY** và có **≥ 1 tin gợi ý** để so sánh, app mở **drawer** gợi ý so sánh thay cho toast “Đã lưu”. Drawer cho phép chọn **2–4 tin** (gồm tin vừa lưu) rồi mở **màn So sánh hiện có (STORY-002)**.

Happy path: AdView → tap Lưu → drawer mở (tin vừa lưu chọn sẵn) → chọn thêm 1–3 tin → tap “So sánh (n/4)” → màn So sánh.

Screens:
| # | Screen | Note |
|---|---|---|
| 1 | AdView PTY + nút Lưu | Màn host hiện có — chỉ đổi phản hồi sau khi lưu / bỏ lưu |
| 2 | Compare suggestion drawer | **Mới** — spec chính |
| 3 | Comparison result | Dùng lại STORY-002, không spec lại |

---

## Display Condition

| Điều kiện | Kết quả |
|---|---|
| User đã login, lưu tin PTY thành công, có ≥ 1 tin gợi ý | Mở drawer |
| Lưu thành công nhưng **0** tin gợi ý | Không mở drawer — giữ **toast lưu tin hiện tại** |
| Chưa login / lưu thất bại | Theo flow production hiện tại (đã define) |
| Bỏ lưu (unsave) | Không mở drawer — snackbar “Đã bỏ lưu.” + “Đến trang Đã lưu” |
| Vertical khác PTY | Không áp dụng |

**Tin gợi ý (PRD):** trùng cả 4 điều kiện với tin vừa lưu — ad type (bán/thuê), category, tỉnh/thành **và** quận/huyện, giá trong **±20%**. Loại trừ: chính tin vừa lưu, tin không còn active (ẩn, hết hạn, gỡ).

## Display Position

- Drawer là **bottom sheet** trên AdView, phủ scrim toàn màn.
- Sheet top cách đỉnh màn **116pt** (status bar + 72); chiều cao = phần còn lại. Header + footer cố định, body cuộn.

---

## Interaction Rules

| Element | Trigger | Behavior |
|---|---|---|
| Nút Lưu (overview / bottom bar / nudge “Lưu tin”) | Tap khi chưa lưu | Gọi API lưu → thành công & có gợi ý → mở drawer; chặn tap lặp tới khi có kết quả |
| Nút Đã lưu | Tap | Bỏ lưu → snackbar “Đã bỏ lưu.” + action “Đến trang Đã lưu” |
| Link “Xem tất cả” | Tap | Đóng drawer → mở Hoạt động › tab **Đã lưu** (`chotot-app://www.chotot.com/activity/da-luu`) |
| Item row (toàn hàng) | Tap | Toggle chọn/bỏ chọn checkbox. **Không** mở AdView |
| Item row khi đã chọn 4 | Tap tin chưa chọn | Không đổi trạng thái, không animation → snackbar “Chỉ được chọn tối đa 4 tin để so sánh” |
| Nút “Đóng” | Tap | Đóng drawer (animation đóng) |
| Scrim | Tap | Đóng drawer |
| Sheet | Vuốt xuống | Đóng drawer |
| Back (Android) | Press | Đóng drawer |
| CTA “So sánh (n/4)” | Tap khi 2 ≤ n ≤ 4 | Mở màn So sánh (STORY-002) với các tin đã chọn, theo thứ tự trong drawer |
| Màn So sánh › Back | Tap | Quay về drawer, giữ nguyên lựa chọn |

## Common Rules

- Tin vừa lưu luôn ở **đầu danh sách**, **chọn sẵn**, user được bỏ chọn.
- n = tổng số tin đang chọn (gồm tin vừa lưu). CTA enabled khi **2 ≤ n ≤ 4**.
- Nguồn tin & thứ tự:
  1. Nhóm: **đã lưu → đã xem (chưa lưu) → tin khác trên Nhà Tốt**. Tin vừa lưu **và** đã xem → nhóm đã lưu.
  2. Trong nhóm: chênh lệch giá tuyệt đối với tin vừa lưu **tăng dần**; bằng nhau → tin đăng **mới hơn** trước.
  3. Tổng tin gợi ý tối đa **10** (không tính tin vừa lưu), cuộn trong drawer.
- Section không có tin → **ẩn cả tiêu đề**.

---

## Layout YAML

```yaml
screen: compare-suggestion-drawer
platform: app
container:
  type: Drawer                       # DS Drawer (bottom sheet)
  scrim: background-overlay (rgba(34,34,34,0.50))
  sheet:
    background: background-primary (#FFFFFF)
    radius-top: radius-modal (20)
    top-offset: 116                   # status bar + 72
    grabber: { width: 36, height: 4, radius: 4, color: border-regular (#DDDDDD), margin-top: spacing-8 }
  children:
    - header:                        # source: .sh-head
        layout: row, align-center, gap: 10   # checkpoint CP-03 → spacing-8
        padding: spacing-16 spacing-16 spacing-12
        children:
          - icon: "[ICON: confirm DS name] success-circle-fill"   # 24, text-success (#12A154)
          - text: { value: "Đã lưu thành công", typo: display-annotation (18/26/700), color: text-primary (#222222), flex: 1 }
          - link: { value: "Xem tất cả", typo: header-caption (14/20/600), color: text-primary (#222222), decoration: underline }
    - body:                          # source: .sh-body — scroll vertical
        children:
          - item-row: just-saved     # selected by default, no section header
          - section-header: "Chọn thêm tin đã lưu"
          - item-row[]: saved
          - section-header: "Chọn thêm tin đã xem - chưa lưu"
          - item-row[]: viewed
          - section-header: "Tin khác trên Nhà Tốt"
          - item-row[]: other
    - footer:                        # source: .sh-foot
        border-top: 1px border-thin (#E8E8E8)
        padding: 10 spacing-16 0      # checkpoint CP-03
        actions:
          layout: row, gap: spacing-8, ratio: 30/70
          - Button: { props: { type: Tertiary, size: Large, label: "Đóng" } }
          - Button: { props: { type: Primary, size: Large, label: "So sánh (n/4)", disabled: "n < 2" } }

section-header:                       # source: .pk-head
  padding: spacing-20 spacing-16 spacing-4
  typo: "17/24/500 — checkpoint CP-01 (proposal body-page)"
  color: text-secondary (#595959)
  divider: none (dùng divider dưới của item phía trên)

item-row:                             # source: .pk-item
  layout: row, align-start, gap: spacing-12
  padding: spacing-12 spacing-16
  background: background-primary (#FFFFFF)
  divider-bottom: 1px border-thin (#E8E8E8)
  hit-area: full row → toggles checkbox
  children:
    - thumbnail:
        size: 100x100
        radius: radius-card-small (8)
        fit: cover
        placeholder: background-tertiary (#E8E8E8)
        overlay-source-icon:          # top 6 / right 6, 22×22, display-only
          saved:  "[ICON: confirm DS name] heart-fill — #F0325E, stroke #FFFFFF 1.6"
          viewed: "[ICON: confirm DS name] heart-outline — fill rgba(0,0,0,.25), stroke #FFFFFF 1.8"
          other:  "heart-outline (như viewed)"
    - info:
        layout: column, gap: 3        # checkpoint CP-03 → spacing-4
        flex: 1
        children:
          - title:  { typo: tagline-caption (14/20/500), color: text-primary (#222222), max-lines: 2, overflow: ellipsis }
          - params: { typo: body-caption (12/18/400), color: text-secondary (#595959), max-lines: 1, format: "{rooms} PN · Hướng {direction} · {type}" }
          - price-row:
              layout: row, align-baseline, gap: spacing-8
              - price: { value: "{size}m² - {price}", typo: header-section (16/24/600), color: text-error (#F0325E) }
              - ppm:   { value: "{price_m2} tr/m²", typo: "13/20/500 — checkpoint CP-02", color: text-primary (#222222) }
          - source: { typo: body-caption (12/18/400), color: text-secondary (#595959), max-lines: 1 }
    - Checkbox:
        props: { size: 24, radius: 6 }  # checkpoint CP-05
        align-self: center
```

## DS Components Used

| Component | Variant / props | Ghi chú |
|---|---|---|
| Drawer | bottom sheet, grabber, scrim | Header/footer cố định, body cuộn |
| Checkbox | override 24×24, radius 6 | CP-05 |
| Button | Primary · Large · radius 8 | “So sánh (n/4)” — PTY brand |
| Button | Tertiary · Large · radius 8 | “Đóng” |
| SnackBar | full width, có/không action | Xem §Content Rules |

## Design Tokens Map

| Usage | Token | Value |
|---|---|---|
| Scrim | background-overlay | rgba(34,34,34,0.50) |
| Sheet, item bg | background-primary | #FFFFFF |
| Thumbnail placeholder | background-tertiary | #E8E8E8 |
| Title, ppm, Tertiary label, header link | text-primary | #222222 |
| Params, source, section header | text-secondary | #595959 |
| Price | text-error | #F0325E |
| Header success icon | text-success | #12A154 |
| Dividers, Tertiary border | border-thin | #E8E8E8 |
| Grabber | border-regular | #DDDDDD |
| Primary button bg (PTY) | button-primary | #FA6819 |
| Primary button label | text-on-background | #FFFFFF |
| Primary hover | interaction-brand-hover | #FB8F4A |
| Primary pressed | interaction-brand-pressed | #E05A10 |
| Primary disabled bg | button-disabled | #C0C0C0 (label #FFFFFF) |
| Tertiary hover / pressed | interaction-neutral-light-hover / -pressed | #E8E8E8 / #DADADA |
| Checkbox checked bg + border | icon-brand (PTY) | #FA6819 |
| Checkbox tick | icon-on-background (PTY) | #FFFFFF |
| Checkbox unchecked border | `[UNMAPPED]` → CP-05 | #C0C0C0 (designer-specified) |
| Snackbar bg | background-inverted | #222222 |

### Non-tokenizable values
| Value | Where | Reason |
|---|---|---|
| Sheet top offset 116 | Drawer | layout-specific |
| Heart overlay fill rgba(0,0,0,.25) | Thumbnail viewed/other | legibility trên ảnh |

## Assets

Không có asset mới. Thumbnail = ảnh tin (user content). Icon dùng DS icon set — CP-04.

---

## Interaction States

### Checkbox
| State | Spec |
|---|---|
| Unchecked | Border 2px #C0C0C0, bg #FFFFFF, tick hidden |
| Checked | Bg + border icon-brand (#FA6819), tick 16px stroke #FFFFFF 3px, round cap/join |
| Focus (a11y) | Outline 2px text-primary, offset 2 |

### Button “So sánh (n/4)” — Primary PTY
| State | Bg | Label |
|---|---|---|
| Default | button-primary #FA6819 | #FFFFFF |
| Hover | interaction-brand-hover #FB8F4A | #FFFFFF |
| Pressed | interaction-brand-pressed #E05A10 | #FFFFFF |
| Disabled (n < 2) | button-disabled #C0C0C0 | #FFFFFF |

### Button “Đóng” — Tertiary
| State | Bg | Border | Label |
|---|---|---|---|
| Default | #FFFFFF | border-thin #E8E8E8 | #222222 |
| Hover | #E8E8E8 | #E8E8E8 | #222222 |
| Pressed | #DADADA | #DADADA | #222222 |

## Content Rules

| Field | Rule |
|---|---|
| Title | Tối đa 2 dòng, ellipsis |
| Params | 1 dòng; thiếu trường nào thì bỏ trường đó + dấu “·” liền kề (không để “· ·”) |
| Price | `{size}m² - {price}`; giá theo format hiện tại của app (tỷ / triệu) |
| Price/m² | `{x} tr/m²`, 2 chữ số thập phân, dấu phẩy |
| Source line | Đã lưu → “Đã lưu · {time}” · Đã xem → “Đã xem · {time}” · Khác → “Tin trên Nhà Tốt” · Tin vừa lưu → vị trí `{district} ({ward})` — time format CP-06 |
| CTA label | “So sánh (n/4)”, n = số tin đang chọn |

### Snackbar (full width, margin-x spacing-16, trên bottom bar/footer)
| Case | Copy | Action | Icon | Duration |
|---|---|---|---|---|
| Chọn tin thứ 5 | Chỉ được chọn tối đa 4 tin để so sánh | — | none | 2s |
| Bỏ lưu | Đã bỏ lưu. | Đến trang Đã lưu | none | 4s |

Style: bg background-inverted (#222222), radius 12, padding spacing-12 × 14, label tagline-caption (14/20/500) #FFFFFF, action label-section (14/20/700) — action color: confirm DS SnackBar action token (prototype dùng #FFD400).

## Edge Cases

| Case | Behavior |
|---|---|
| 0 tin gợi ý | Không mở drawer, giữ toast lưu tin hiện tại |
| Chỉ có 1–2 nhóm có tin | Ẩn section rỗng (cả tiêu đề) |
| Không có lịch sử lưu/xem | Chỉ tin vừa lưu + “Tin khác trên Nhà Tốt” |
| > 10 tin gợi ý | Cắt còn 10 theo thứ tự §Common Rules |
| Bỏ chọn tin vừa lưu | Cho phép; n giảm, CTA disabled nếu n < 2 |
| Đạt 4 tin | Tin khác vẫn hiển thị bình thường; tap → snackbar giới hạn |
| Tap Lưu liên tục | Chỉ gọi API & mở drawer 1 lần |
| Danh sách đang tải | Mở drawer với tin vừa lưu, phần gợi ý dùng DS loading/skeleton platform |
| Chưa login / lưu lỗi / trạng thái tin / case màn So sánh | Đã define ở project khác — giữ nguyên |

---

## Tagging & Analytics

Proposal — CP-09 (PM/Data chốt tên & schema):
| Event | When | Params gợi ý |
|---|---|---|
| `save_ad_compare_drawer_show` | Drawer hiển thị | ad_id, n_saved, n_viewed, n_other |
| `save_ad_compare_drawer_item_select` / `_unselect` | Toggle tin | ad_id, source (saved/viewed/other), position |
| `save_ad_compare_drawer_limit_reached` | Chạm tin thứ 5 | ad_id |
| `save_ad_compare_drawer_submit` | Tap “So sánh (n/4)” | ad_ids, n |
| `save_ad_compare_drawer_view_saved` | Tap “Xem tất cả” | — |
| `save_ad_compare_drawer_close` | Đóng | method (button/scrim/swipe/back) |

Màn So sánh dùng lại event STORY-002 (`screen_view_compare_result`, `save_ad_compare_result_*`).

---

## Prototype Quality

| Hạng mục | Đánh giá |
|---|---|
| Naming / structure | ✅ class có nghĩa (.sh-head, .pk-item, .pk-cb…), DOM ≤ 5 tầng/cụm |
| Token binding | ⚠️ Một phần dùng CSS var; nhiều màu viết hex trực tiếp — đã map tay ở §Tokens |
| `data-ds-*` annotations | ❌ Chưa có — component/variant suy luận + xác nhận qua interview |
| Interaction coverage | ✅ Prototype tương tác đủ happy path, giới hạn 4, đóng drawer, snackbar |
| Figma | Figma cũ (có X, tag “Tin vừa lưu”, CTA “So sánh (n)”) — bỏ qua, theo spec này |

**Quality Score:** 84 / 100 — ⚠️ READY WITH NOTES (Intent 36/40 · Edge 25/30 · Interview 17/20 · Prototype 6/10)

## Animations (overrides default)

`easing.spring = cubic-bezier(.34, 1.56, .64, 1)`

| Event | Spec |
|---|---|
| Drawer open | Sheet translateY 100% → 0, 300ms `cubic-bezier(.2,.8,.2,1)`; scrim opacity 0 → 1, 200ms ease |
| Drawer close | Sheet translateY 0 → 100%, 250ms `cubic-bezier(.4,0,1,1)`; scrim 1 → 0, 250ms ease; block input khi đang đóng |
| checkbox.enter | Mở drawer: scale 0.4 → 1, 320ms spring, stagger 25ms/item (item k trễ k×25ms) |
| checkbox.color | Bg + border 160ms ease; tick hiện/ẩn ngay (không fade) |
| checkbox.pop | Khi **chọn**: scale 1 → 1.12 (320ms spring), giữ 150ms, → 1 (320ms spring) |
| card.press | Khi **chọn**: row scale 1 → 0.985 → 1, mỗi chiều 260ms spring |
| cta.bump | Mỗi lần n đổi (chọn & bỏ chọn): 1 → 1.04 → 1, mỗi chiều 260ms spring |
| Bỏ chọn | Chỉ checkbox.color + cta.bump |
| Over limit | Không animation |
| Snackbar | opacity 0 → 1 + translateY 12 → 0, 250ms |
| Reduce Motion | Tắt toàn bộ, state vẫn đổi đúng |

Easing per platform:
| Curve | iOS | Android (View) | Compose |
|---|---|---|---|
| spring `(.34,1.56,.64,1)` | `CAMediaTimingFunction(controlPoints: 0.34, 1.56, 0.64, 1)` | `PathInterpolator(0.34f, 1.56f, 0.64f, 1f)` | `CubicBezierEasing(0.34f, 1.56f, 0.64f, 1f)` |
| open `(.2,.8,.2,1)` | `CAMediaTimingFunction(controlPoints: 0.2, 0.8, 0.2, 1)` | `PathInterpolator(0.2f, 0.8f, 0.2f, 1f)` | `CubicBezierEasing(0.2f, 0.8f, 0.2f, 1f)` |
| close `(.4,0,1,1)` | `CAMediaTimingFunction(controlPoints: 0.4, 0, 1, 1)` | `PathInterpolator(0.4f, 0f, 1f, 1f)` | `CubicBezierEasing(0.4f, 0f, 1f, 1f)` |
| ease | `.curveEaseInOut` | `AccelerateDecelerateInterpolator` | `FastOutSlowInEasing` |

Motion reference: prototype trên canvas (Play `Compare1Tap.dc.html`).

## Accessibility

- Item row = 1 phần tử có role checkbox, label = title + giá + nguồn; state checked/unchecked.
- Chạm tin thứ 5: announce nội dung snackbar.
- Tap target tối thiểu 44pt (row, buttons, link).
- Drawer mở: focus vào title “Đã lưu thành công”; đóng → focus về nút Lưu.
- Reduce Motion: xem §Animations.

## Known DS Gotchas

- PTY primary là **cam (#FA6819) chữ trắng** — không dùng vàng Chợ Tốt.
- Checkbox checked theo brand PTY → tick **trắng** (icon-on-background), không phải #222.
- Disabled Primary dùng button-disabled (#C0C0C0) + chữ trắng — không giảm opacity.
- Drawer không có nút X (khác Figma cũ).

## Verify Checklist

- [ ] Lưu tin PTY có gợi ý → drawer mở thay toast; không gợi ý → toast cũ.
- [ ] Tin vừa lưu ở đầu, chọn sẵn, bỏ chọn được; không có tag “Tin vừa lưu”.
- [ ] 3 section đúng thứ tự, section rỗng ẩn, tối đa 10 tin gợi ý, thứ tự theo chênh lệch giá.
- [ ] Dòng nguồn đúng copy + thời gian.
- [ ] CTA “So sánh (n/4)” disabled khi n < 2; mở màn So sánh với tin đã chọn; Back giữ lựa chọn.
- [ ] Đạt 4 tin: tin khác không disable, tap → snackbar giới hạn, không animation.
- [ ] Đóng drawer bằng Đóng / scrim / vuốt / Back, có animation đóng.
- [ ] Bỏ lưu → snackbar “Đã bỏ lưu.” + “Đến trang Đã lưu”.
- [ ] Màu Primary/Checkbox theo PTY; snackbar full width margin 16.
- [ ] Motion đúng token; Reduce Motion tắt animation.
