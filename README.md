# TL-Forge Household Planner

A Python-only control desk for MMORPG world designers to manage professions, city districts, and AI-assisted household generation without any external database or Docker runtime.

## Features

- **Profession Registry:** Create, update, and delete the list of allowed occupations directly from the NiceGUI workspace.
- **District Manager:** Define districts with textual lore, notes, and target household counts; trigger AI-backed generation per district or in batch.
- **GPT Co-Pilot:** Every generation step (household layout, demographics, member roster, quality review) flows through the ChatGPT API when credentials are provided, falling back to a deterministic offline stub for local testing. All prompts and answers are logged to local memory for auditing.
- **Threaded Generation:** Each district runs on its own worker thread to ensure quick feedback and independent retries.
- **Editable Results:** Generated households and family members can be inspected, pruned, or replaced in the UI before exporting.
- **Excel Export:** Download the latest households and members into an Excel workbook for further design work.

## Getting Started

1. **Install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Optional: Configure ChatGPT**

   Set environment variables if you want to use the real API:

   ```bash
   export OPENAI_API_KEY=sk-...
   export OPENAI_MODEL=gpt-4o-mini  # or preferred
   ```

   Without credentials the app uses a deterministic offline generator so tests and demos still run.

3. **Run the backend**

   ```bash
   uvicorn api.main:app --reload
   ```

4. **Launch the UI**

   ```bash
   python -m ui.app
   ```

   The UI consumes the FastAPI endpoints at `http://localhost:8000` by default; configure a reverse proxy if necessary.

## Tests

Run the automated checks with:

```bash
pytest
```

The test suite verifies CRUD flows and the offline generation pipeline.

## Data Storage

All state lives in JSON files inside `data/`. You can relocate them by setting:

- `TLFORGE_DATA_DIR`
- `TLFORGE_STATE_FILE`
- `TLFORGE_MEMORY_FILE`

These folders are created automatically on first run.

## Export

Use the **Tải Excel** button in the UI or perform a direct GET request to `/api/export/excel` to receive the workbook with two sheets (`Households`, `Members`).
