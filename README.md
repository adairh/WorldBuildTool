# TL-Forge Toolkit — Python-Only, File-Backed Edition

"Tôi đang làm worldbuild cho Thăng Long" nghĩa là chúng ta cần cả một xưởng công cụ để giữ cho
phường phố, gia tộc, lễ hội và nhiệm vụ luôn sống động. Bản refactor này gom toàn bộ dự án vào một
stack Python thuần, không Docker, không cơ sở dữ liệu – tất cả dữ liệu được lưu thành JSON/CSV trong
thư mục `storage/`. Bộ công cụ được chia thành bốn trụ chính để hỗ trợ sản xuất nội dung cho một
Vietnam Wuxia MMORPG.

## Bộ công cụ cuối cùng (Bức tranh tổng)

### A. Map & Spatial
- **Map Annotator**: tạo marker GeoJSON, phân lớp (architecture/economy/religion/social), xuất dữ liệu.
- **Tile & Historical Overlay**: tải ảnh nền, chồng lớp bản đồ cổ (dùng file nội bộ).
- **Procedural District Layout**: sinh khu phố theo seed, dựa trên quy tắc phường nghề.
- **POI Dependency Manager**: kiểm tra ràng buộc (chợ ↔ sông, đình ↔ trung tâm phường).

### B. People & Lore
- **Household / NPC Generator**: sinh hộ dân, nghề nghiệp, gốc gác; lưu thành JSON + CSV.
- **Relationship Graph Viewer**: xuất dữ liệu mạng quan hệ để cytoscape/d3 xử lý.
- **Dialogue / Quest Node Editor**: viết hội thoại phân nhánh, xuất JSON.
- **Name Generator**: seedable, theo khu vực/đình/giáp.

### C. Assets & Media
- **Asset Tracker**: quản lý tag, phiên bản, moodboard.
- **Prompt Refiner & Batch Prompting**: sinh prompt AI theo biến thể.
- **Concept Review Board**: bảng duyệt/nhận xét.
- **Image Reference Geotagger**: gắn reference vào POI.

### D. Simulation & Export
- **Timeline Manager**: kéo-thả sự kiện, kiểm tra phụ thuộc.
- **Economy Simulator**: nhập sản lượng → dòng chảy thuế, thương mại.
- **Event Randomizer / Scheduler**: sinh sự kiện theo mùa/ngày.
- **Exporter & Consistency Checker**: tạo gói JSON/CSV/Unity ScriptableObject.

## Ưu tiên cao (đổi cuộc chơi ngay)
1. **Map Annotator** (GeoJSON + layer) – neo mọi thông tin không gian.
2. **Household/NPC Generator + Relationship Graph** – dựng xã hội, cung cấp dữ liệu nhiệm vụ.
3. **Timeline Manager** – giữ lịch sử đồng bộ.
4. **Exporter + Consistency Checker** – đưa dữ liệu vào Unity hoặc pipeline dev.

## MVP cho từng tool
| Tool | Tính năng tối thiểu |
|------|--------------------|
| Map Annotator | Upload ảnh nền, tạo marker (type/tags/description/images), bật/tắt layer, export GeoJSON |
| NPC Generator | Nhập số hộ + seed, sinh hộ dân, cho phép chỉnh sửa, export JSON + CSV |
| Timeline | Thêm sự kiện (ISO date), mô tả, liên kết POI/NPC, filter theo giai đoạn, export CSV/JSON |
| Exporter | Chọn loại dữ liệu (NPC/POI/Event), xuất JSON/CSV/Unity JSON |

## Repository Structure
```
api/
  config.py          # cấu hình và thư mục lưu trữ
  storage.py         # helper đọc/ghi JSON cục bộ
  models/            # Pydantic models cho POI, household, person, event, asset, quest
  routers/           # FastAPI routers (pois, households, events, export)
  services/          # nghiệp vụ: generator, checker, exporter, map annotator helpers
  main.py            # FastAPI app
ui/
  app.py             # NiceGUI shell
  components/        # view cho Map, People, Timeline, Exporter, Assets
storage/             # sinh trong runtime (git ignored)
docs/                # tài liệu bổ sung
requirements.txt     # chỉ Python packages (không Docker)
```

## Thiết lập môi trường
```bash
python -m venv .venv
source .venv/bin/activate  # hoặc .venv\Scripts\activate trên Windows
pip install --upgrade pip
pip install -r requirements.txt
```

Chạy API:
```bash
uvicorn api.main:app --reload
```

Chạy UI NiceGUI (sử dụng cùng services và storage):
```bash
python -m ui.app
```

## Lưu trữ và dữ liệu mẫu
- Tất cả dữ liệu nằm trong `storage/` (tự tạo nếu chưa tồn tại).
- `storage/pois.json`, `storage/households.json`, `storage/persons.json`, `storage/events.json`.
- Xuất khẩu được lưu tại `storage/exports/` (JSON, CSV, Unity-style JSON).

Ví dụ hộ dân:
```json
{
  "household_id": "HH-001",
  "location": {"poi_id": "POI-045", "x": 1240, "y": 820},
  "members": [
    {"person_id": "P-0001", "name": "Trần Văn Cẩn", "birth_year": 1250, "sex": "M", "profession": "thương nhân"},
    {"person_id": "P-0002", "name": "Nguyễn Thị Mỵ", "birth_year": 1255, "sex": "F", "profession": "dệt vải"},
    {"person_id": "P-0003", "name": "Trần Thị Lan", "birth_year": 1272, "sex": "F", "relation": "con"}
  ],
  "house_type": "nhà 3 gian",
  "notes": "sống gần chợ Tế Xuyên"
}
```

Ví dụ POI (GeoJSON-like):
```json
{
  "type": "Feature",
  "id": "POI-045",
  "geometry": {"type": "Point", "coordinates": [106.258, 10.396]},
  "properties": {
    "name": "Chợ Tế Xuyên",
    "layers": ["economy", "transport"],
    "description": "chợ chính quận Đông",
    "tags": ["grain", "textile"]
  }
}
```

## API Surface (python-only, file-backed)
- `GET /pois`, `POST /pois`, `PUT /pois/{poi_id}` – quản lý marker và layers.
- `POST /households/generate` – sinh hộ dân theo `{count, seed, poi_pool}`.
- `GET /households` – đọc dữ liệu đã lưu.
- `POST /events` / `GET /events` – quản lý timeline.
- `POST /export` – `{types:["pois","persons","households","events"], format:"json"|"csv"|"unity"}` → trả đường dẫn file.
- `POST /checker/validate` – trả danh sách vấn đề (tuổi, trùng id, liên kết POI thiếu).

## UI Wireframe (Map Annotator)
```
┌────────────────────────────────────────────────────────────────┐
│ Project: Thăng Long | Search | Export                          │
├─────────────┬──────────────────────────────┬───────────────────┤
│ Layers      │ Map Canvas                   │ Details           │
│ [x] Arch    │ (zoom/pan, markers clickable)│ Name, Type        │
│ [ ] Econ    │                              │ Description       │
│ [x] Rel     │                              │ Tags, Images      │
│ [x] Social  │                              │ Linked households │
│ POI list    │                              │ Save / Delete     │
├─────────────┴──────────────────────────────┴───────────────────┤
│ Quick actions: Add POI | Snap household | Generate households │
└────────────────────────────────────────────────────────────────┘
```

## Testing
```bash
pytest
```
Các bài test chỉ dựa vào file JSON nội bộ nên chạy được ngay cả khi thiếu FastAPI/NiceGUI trong môi trường CI đơn giản.

## Lộ trình triển khai
- **Phase A**: Map Annotator MVP, NPC Generator, Exporter JSON/CSV.
- **Phase B**: Relationship Graph, Timeline nâng cao, Asset Tracker.
- **Phase C**: Kinh tế mô phỏng, Event randomizer, Unity importer hoàn chỉnh.

## Quick next steps
1. Yêu cầu JSON schema đầy đủ (NPC/POI/Event/Asset) + sample data.
2. Sinh tài liệu OpenAPI từ FastAPI để frontend dựng client.
3. Xuất UI mockup chi tiết cho Map Annotator + NPC editor.

