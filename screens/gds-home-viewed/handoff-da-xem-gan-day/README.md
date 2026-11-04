# Handoff · Trang chủ · "Đã xem gần đây" (T1 + T2)

## Còn thiếu / cần chốt trước QC
- ⚠️ **Tracking:** tên event và dimension mới chỉ là đề xuất (xem §Tagging & Analytics trong spec). Owner: PM/Data.
- ⚠️ **Tỉ lệ AB:** chưa chốt tỉ lệ Control / T1 / T2. Owner: PM.
- ⚠️ **T2 vùng bấm:** spec chốt bấm cả thẻ; prototype trong gói vẫn chỉ cho bấm nút. Build theo spec.
- Không có minh hoạ cần export. Ảnh tin là dữ liệu thật của user.

## Gói có gì
| Đường dẫn | Nội dung |
|---|---|
| `designspec-da-xem-gan-day.md` | Spec chính (đọc trước) |
| `assets/icons/` | 2 icon DS của section: `Chevronright-outline.svg`, `Arrowright-outline.svg` (fill = currentColor) |
| `assets/section-render/` | Ảnh render riêng cụm section T1 (375×240) và T2 (375×110) @1x/@2x/@3x — để QA so sánh, không dùng trong app |
| `assets/demo-listing-photos/` | Ảnh tin mẫu, chỉ để dựng mock |
| `prototype/` | HTML tĩnh chạy offline: `t1-home.html`, `t2-home.html`, `t1-hoat-dong.html`, `t2-hoat-dong.html` + ảnh chụp `.png` |

## Phạm vi
Chỉ section "Đã xem gần đây". Phần còn lại của Trang chủ và màn "Hoạt động › Xem gần đây" là màn có sẵn, chỉ để tham chiếu. Đã bỏ trạng thái skeleton: loading dùng mặc định DS của từng nền tảng.

## Nguồn
Design canvas "Tin đăng đã xem · Trang chủ", page "SaveAd section", artboard `MainSave.dc.html`. Design owner: Lâm Phan.
