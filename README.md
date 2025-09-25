# TL-Forge Toolkit — Python-Only, File-Backed Edition

"Tôi đang làm worldbuild cho Thăng Long" nghĩa là chúng ta cần cả một xưởng công cụ để giữ cho
phường phố, gia tộc, lễ hội, bãi quái, trang bị và hoạt động luôn sống động. Phiên bản mới gom toàn
bộ dự án vào một stack Python thuần, không Docker, không cơ sở dữ liệu – tất cả dữ liệu được lưu
thành JSON/CSV trong thư mục `storage/`. TL‑Forge giờ là bàn điều khiển AAA trọn vẹn cho một Vietnam
Wuxia MMORPG: narrative, gameplay, economy, QA đồng bộ chỉ với Python + file.

> 🎯 **Dành cho nhà thiết kế AAA**: xem thêm tài liệu "[TL-Forge — AAA Designer Command Desk](docs/designer_spec.md)"
> để nắm trải nghiệm người dùng, các overlay bắt buộc, rulebook và định nghĩa hoàn thành từ góc nhìn
> đội thiết kế game.

## Bộ công cụ cuối cùng (Bức tranh tổng)

### A. Map & Spatial Warfare
- **Map Annotator**: tạo marker GeoJSON, phân lớp (architecture/economy/religion/social), xuất dữ liệu.
- **Monster Zone Overlay**: polygon spawn zone, heatmap cấp độ, encounter style breakdown.
- **Procedural District Layout**: sinh khu phố theo seed, dựa trên quy tắc phường nghề.
- **POI Dependency Manager**: kiểm tra ràng buộc (chợ ↔ sông, dungeon ↔ hub, patrol ↔ gate).

### B. Story, Quest & Cinematic Control
- **Story Arc Manager**: arc main/faction/class/seasonal, coverage auto-sync map & timeline.
- **Quest Graph Editor**: node thoại, lựa chọn, condition, variety checker combat/social/puzzle.
- **Narrative Coverage Dashboard**: hub nào còn trống, cinematic hook nào cần dựng.
- **Approval Pipeline**: LGD approve arc, ND approve dialogue, QA xem diff.

### C. Combat Features & Live Activities
- **Monster Camp Designer**: spawn pool, faction link, event hook (đêm/mùa/invasion).
- **Gameplay Feature Library**: Arena, Quest Board, Crafting Station, Dungeon Entrance, PvP Zone, Festival.
- **Activity Scheduler**: daily/weekly/seasonal mini-game, quest board, community events.
- **Encounter Variety Analytics**: combat/social/puzzle ratio theo hub và zone.

### D. Loot, Economy & Export
- **Household / NPC Generator**: sinh hộ dân, ledger kinh tế, nghề, rep.
- **Loot & Item Tables**: nguồn rơi từ quest/monster/feature/activity, progression timeline.
- **Timeline & Shock Simulator**: sự kiện lịch sử, bão, trade fair ảnh hưởng kinh tế.
- **Exporter & Rulebook Checker**: JSON/CSV/Unity + rule violations realtime.

## Ưu tiên cao (đổi cuộc chơi ngay)
1. **Command Desk Dashboard** – realtime coverage, rulebook, export readiness.
2. **Story Arc + Quest Graph** – kéo thả arc, sync map/timeline, cinematic checklist.
3. **Monster Zone + Feature Planner** – heatmap cấp độ, coverage hub × feature.
4. **Loot & Activity Systems** – loot source health, activity cadence, economy snapshot.

## MVP cho từng tool
| Tool | Tính năng tối thiểu |
|------|--------------------|
| Command Desk | Dashboard coverage/story/feature/loot, refresh seed, expose rule issues |
| Story Arc Builder | Sinh questline + arc, tính coverage, đánh dấu cinematic, export JSON |
| Monster & Feature Planner | Vẽ zone polygon, chọn pool quái, gắn feature hub, heatmap variety |
| Loot & Activity Scheduler | Lập bảng item drop, lịch hoạt động daily/weekly/seasonal |
| Exporter | Chọn loại dữ liệu (POI/Quest/Zone/Item/Activity), xuất JSON/CSV/Unity JSON |

## Repository Structure
```
api/
  config.py          # cấu hình và thư mục lưu trữ
  storage.py         # helper đọc/ghi JSON cục bộ
  models/            # Pydantic models cho POI, household, quest, story arc, monster zone, loot, activity
  routers/           # FastAPI routers (world, pois, households, quests, story, monsters, features, items, activities, export)
  services/          # nghiệp vụ: generator, checker, exporter, dashboard analytics
  main.py            # FastAPI app
ui/
  app.py             # NiceGUI shell
  components/        # view cho Command Desk, Story, Encounters, Gameplay, Loot, QA
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
- `storage/pois.json`, `storage/households.json`, `storage/persons.json`, `storage/events.json`,
  `storage/quests.json`, `storage/story_arcs.json`, `storage/monster_zones.json`,
  `storage/features.json`, `storage/items.json`, `storage/activities.json`.
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
- `POST /world/regenerate` – tái tạo toàn bộ dataset (POI, quest, arc, zone, feature, item, activity).
- `GET /world/dashboard` – coverage %, encounter breakdown, loot distribution, export readiness.
- `GET/POST /quests` – quản lý quest graph.
- `GET/POST /story/arcs` – quản lý arc coverage.
- `GET/POST /monsters/zones` – zone spawn & encounter variety.
- `GET/POST /features` – gameplay feature placement.
- `GET/POST /items` – loot tables từ quest/monster/feature/activity.
- `GET/POST /activities` – lịch hoạt động daily/weekly/seasonal.
- `POST /households/generate`, `GET /households` – dữ liệu dân cư.
- `GET/POST /events` – timeline lịch sử.
- `POST /export` – `{types:[...], format:"json"|"csv"|"unity"}` → trả đường dẫn file.
- `GET /checker/summary` – rulebook issues + metrics.

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

