# TL-Forge Toolkit — Python Only, Fully Customisable

> “Tôi đang làm worldbuild cho Thăng Long và tôi muốn làm chủ mọi chi tiết.” TL‑Forge phiên bản mới
> biến yêu cầu đó thành một bàn làm việc số hoàn toàn Python: không Docker, không database, mọi dữ
> liệu nằm trong thư mục `storage/` dạng JSON. Designer có thể tải ảnh bản đồ riêng, đặt POI thủ
> công, quản lý hộ gia đình, questline, sự kiện và asset ngay trong giao diện NiceGUI, đồng thời sử dụng
> API FastAPI để tự động hóa khi cần.

## Những gì bạn có được

| Trụ cột | Công cụ chính | Mô tả |
|---------|---------------|-------|
| **Command Desk** | Dashboard & Notes | Thống kê POI, hộ, NPC, quest, sự kiện; xem coverage từng layer; đọc ghi chú thế giới. |
| **Map Studio** | Map Annotator | Upload ảnh bản đồ (PNG/JPG), click chọn toạ độ trên ảnh để tạo/điều chỉnh POI, quản lý layer & tag. |
| **People Studio** | Household Editor | Tạo hộ dân, chỉnh danh sách thành viên, gán POI nơi ở, ghi chú, xoá hoặc cập nhật bất kỳ lúc nào. |
| **Timeline Studio** | Event Planner | Ghi timeline theo ngày (ISO), liên kết POI, gắn tag festival/biến cố, chỉnh sửa trực tiếp. |
| **Quest Studio** | Quest Graph + Prompt Craft | Soạn quest thủ công với từng bước hoặc nhập prompt để TL‑Forge dựng nhanh outline (có seed để reproducible). |
| **Asset Library** | Asset Tracker | Theo dõi concept art, âm thanh, cinematic… với tag, owner, trạng thái, đường link reference. |
| **AI Co-Pilot** | Prompt Console | Gửi prompt ChatGPT, xem bộ nhớ từng channel, sử dụng lại gợi ý lore ngay trong UI. |

Mọi thao tác đều cập nhật ngay vào JSON, nên bạn có thể commit cùng branch worldbuild hoặc xuất ra Unity/engine khác.

## Kiến trúc gọn nhẹ

```
api/
  config.py          # cấu hình thư mục lưu trữ
  models/            # Pydantic models cho WorldState, POI, Household, Quest, Event, Asset
  routers/           # FastAPI endpoints: world, pois, households, quests, events, assets
  services/          # world_state (CRUD file), storycraft (prompt -> quest), exporter
  main.py            # FastAPI app
ui/
  app.py             # NiceGUI shell với các tab studio
  components/        # world.py, map.py, people.py, timeline.py, quests.py, assets.py, ai.py
storage/             # sinh trong runtime (git ignored)
requirements.txt     # chỉ các package Python cần thiết
```

## Cài đặt & chạy

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Chạy API (tùy chọn nếu muốn dùng REST hoặc tích hợp công cụ khác):

```bash
uvicorn api.main:app --reload
```

Chạy giao diện TL‑Forge:

```bash
python -m ui.app
```

Tất cả dữ liệu sẽ lưu tại `storage/`. Ảnh bản đồ tải lên nằm trong `storage/media/`. Export JSON mặc định lưu tại `storage/world_export.json` (có thể đổi đường dẫn qua service).

## Workflow mẫu

1. **Tải ảnh bản đồ** – vào Map Studio, upload file PNG/JPG. TL‑Forge chuyển thành data URL để hiển thị; có thể click chọn toạ độ trực tiếp.
2. **Đặt POI** – tạo điểm mới, nhập tên, layer, tag; chọn lại vị trí bằng công cụ “Chọn trên bản đồ”.
3. **Tạo hộ dân** – sang People Studio, thêm hộ mới, nhập thành viên, gán POI cư trú.
4. **Ghi timeline** – mỗi sự kiện nhập ngày ISO (VD `1285-08-15`), liên kết POI và tag.
5. **Dựng quest** – soạn tay hoặc nhập prompt để hệ thống gợi ý chuỗi bước; có thể chỉnh lại từng bước (encounter, POI, NPC) trước khi lưu.
6. **Quản lý asset** – theo dõi concept/moodboard/âm thanh, gắn tag và status.
7. **Xuất dữ liệu** – gọi API `POST /world/export` hoặc dùng module `api.services.export_world()` để lấy JSON phục vụ engine khác.

## API rút gọn

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET`  | `/world` | Nhận toàn bộ `WorldState` (map, poi, households, quests, events, assets). |
| `GET`  | `/world/summary` | Trả thống kê tổng hợp (số lượng, coverage layer). |
| `POST` | `/world/export` | Xuất JSON hiện tại, trả về đường dẫn file trong `storage/`. |
| `GET/POST/PUT/DELETE` | `/pois` | CRUD điểm mốc. |
| `GET/POST/PUT/DELETE` | `/households` | CRUD hộ dân. |
| `GET/POST/PUT/DELETE` | `/events` | CRUD sự kiện timeline. |
| `GET/POST/PUT/DELETE` | `/quests` | CRUD quest; `POST /quests/craft` tạo quest từ prompt. |
| `GET/POST/PUT/DELETE` | `/assets` | CRUD asset/media tracker. |
| `POST` | `/ai/prompt` | Gửi prompt cho ChatGPT (ghi nhớ theo channel, lưu lịch sử cục bộ). |
| `GET/DELETE` | `/ai/memory` / `/ai/memory/{channel}` | Đọc hoặc xoá bộ nhớ AI lưu tại `storage/chat_memory.json`. |

Tất cả endpoint chỉ thao tác trên file JSON, nên có thể dùng trong automation/script mà không cần DB.

## ChatGPT & bộ nhớ cục bộ

TL‑Forge Python edition mặc định tích hợp ChatGPT cho mọi thao tác cần "lore hoá": mô tả POI, ghi chú hộ dân, nghề nghiệp, mô tả sự kiện, asset, quest synopsis và AI Co-Pilot. Thiết lập:

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini         # tuỳ chọn, mặc định gpt-4o-mini
OPENAI_TEMPERATURE=0.7           # tuỳ chọn
CHAT_MEMORY_FILE=chat_memory.json
CHAT_MEMORY_LIMIT=24             # số lượt lưu mỗi channel
```

- Bộ nhớ hội thoại lưu trong `storage/{CHAT_MEMORY_FILE}` để có thể xem lại, xoá theo channel qua API hoặc tab "AI Co-Pilot".
- Nếu muốn chạy offline (ví dụ khi CI), đặt `TLFORGE_FAKE_AI=1`. Hệ thống sẽ sinh mô tả deterministic và gắn nhãn `[Offline AI]`.
- Các endpoint `/ai/prompt` và `/ai/memory` giúp công cụ ngoài (hoặc UI) gửi prompt, xem lịch sử.

## Testing

```bash
pytest
```

Các bài test dùng fixture `tmp_path` để tạo thư mục storage tạm, đảm bảo chạy độc lập với dữ liệu thật.

## Ghi chú thiết kế

- Các model sử dụng Pydantic v2 (`BaseModel`) nên chạy trên Python 3.10+.
- File JSON được format đẹp (indent=2, UTF-8) giúp diff trên git dễ đọc.
- Khi cần reset toàn bộ dữ liệu, chỉ việc xoá nội dung `storage/`.
- NiceGUI cho phép mở rộng nhanh: bạn có thể thêm tab mới (ví dụ “Economy Lite”) bằng cách viết component và import vào `ui/app.py`.

Chúc bạn dựng nên một Thăng Long sống động – hoàn toàn chủ động, từng click đều được lưu giữ.
