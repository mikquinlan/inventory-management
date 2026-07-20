# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Factory Inventory Management System demo — Vue 3 frontend, Python FastAPI backend, in-memory mock data loaded from JSON (no database).

> ⚠️ **This repository and any fork you create are PUBLIC.** Do not commit credentials, internal hostnames, or private registry URLs. `client/.npmrc` pins the public npm registry and `client/package-lock.json` is gitignored to prevent locally-configured registries from leaking into commits — leave both in place.

## Critical Tool Usage Rules

### Subagents

- **vue-expert**: Vue 3 frontend features, UI components, styling, client-side functionality.
  **MANDATORY: any time you create or significantly modify a `.vue` file, delegate to vue-expert.**
- **code-reviewer**: after writing significant code.
- **Explore**: understanding codebase structure, searching for patterns.
- **general-purpose**: complex multi-step tasks that don't fit the above.

### Skills

- **backend-api-test**: use when writing or modifying tests in `tests/backend`.

### MCP Tools

- **ALWAYS use GitHub MCP tools** (`mcp__github__*`) for ALL GitHub operations.
  Exception: local branches — use `git checkout -b`, not `mcp__github__create_branch`.
- **ALWAYS use Playwright MCP tools** (`mcp__playwright__*`) for browser testing, against `http://localhost:3000` (frontend) and `http://localhost:8001` (API).

## Commands

```bash
# Both servers (macOS/Linux)
./scripts/start.sh          # backend :8001, frontend :3000, docs :8001/docs
./scripts/stop.sh

# Backend only
cd server && uv sync && uv run python main.py

# Frontend only
cd client && npm install && npm run dev
npm run build               # output: client/dist/
```

Tests (backend only — there is no frontend test runner):

```bash
cd tests
uv run --project ../server pytest -v                          # all 40 tests
uv run --project ../server pytest backend/test_inventory.py -v
uv run --project ../server pytest backend/test_inventory.py::TestInventoryEndpoints::test_get_all_inventory -v
uv run --project ../server pytest --cov=../server --cov-report=html
```

`tests/` has no `pyproject.toml`, so a bare `uv run pytest` there fails with `Failed to spawn: pytest` — `--project ../server` is required (`tests/README.md` omits it and is wrong on this point, as well as on the test count: it describes a `test_orders.py` that does not exist). `pytest.ini` sets `testpaths = backend`, so the working directory must still be `tests/`. `conftest.py` puts `server/` on `sys.path` and exposes a `client` fixture (FastAPI `TestClient`) — tests import `main` directly, so no server needs to be running.

## Architecture

**Request path**: `useFilters` composable → `client/src/api.js` (axios, query params) → FastAPI endpoint → in-memory list filtering → Pydantic `response_model` validation → Vue `ref` → `computed` for anything derived.

**Backend** (`server/main.py`, ~300 lines, single module):

- `mock_data.py` loads every `server/data/*.json` at import time into module-level lists. Data is read-only in practice; mutations don't persist and a restart reloads from disk.
- Two shared helpers do most of the work: `filter_by_month(items, month)` (accepts both `2025-01` and `Q1-2025`) and `apply_filters(items, warehouse, category, status, month)`. New filterable endpoints should reuse them rather than re-implementing.
- Filter convention: every filter param is `Optional[str]` and the literal string `'all'` means "no filter". Category matching is case-insensitive.
- Pydantic models live at the top of `main.py`. **Changing a JSON data file's shape requires updating the matching model**, or the endpoint 500s on response validation.

**Frontend** (`client/src/`):

- Routes declared inline in `main.js`; views in `views/`, shared UI in `components/`. `App.vue` holds the global stylesheet and layout chrome — component styles are `scoped`.
- Three composables use a **module-scope singleton** pattern: state refs are declared _outside_ the exported function, so every caller shares one instance.
  - `useFilters.js` — global filter state. Note the naming mismatch: UI-side `selectedLocation` maps to the API's `warehouse` param, and `selectedPeriod` maps to `month`. `getCurrentFilters()` performs that translation; call it instead of building filter objects by hand.
  - `useI18n.js` — `en`/`ja` from `locales/*.js`, dot-path `t('a.b.c')` lookup with English fallback, locale persisted in `localStorage` under `app-locale`.
  - `useAuth.js` — mock user; several fields are locale-derived, so it depends on `useI18n`.
- **Currency is derived from locale, not chosen separately**: `en` → USD, `ja` → JPY (`useI18n.js`). All amounts are stored as USD in the JSON data; `utils/currency.js` converts at a hardcoded `USD_TO_JPY = 150`. Render money through `formatCurrency(amount, currentCurrency)`, never a hardcoded `$`.
- `api.js` hardcodes `http://localhost:8001/api` — there is no Vite proxy, so the backend must actually be up on 8001 for the frontend to show data.

**Directory-level guidance**: `server/CLAUDE.md` and `client/CLAUDE.md` carry detailed backend and frontend conventions; read the relevant one before non-trivial work in that directory.

## Gotchas

1. `v-for` keys must be stable IDs (`sku`, `id`, `month`) — never the array index.
2. Validate dates before `.getMonth()` — mock data contains rows with missing/invalid dates.
3. `/api/inventory` has no month filter: inventory has no time dimension. Passing `month` to it is a silent no-op.
4. Revenue goals used by Dashboard/Reports: $800K per month, $9.6M YTD across all months.
5. `views/Backlog.vue` is dead code — no route in `main.js` and nothing imports it. Backlog data is surfaced through `Dashboard.vue` instead.
6. Data files must stay cross-consistent: SKUs referenced by orders must exist in `inventory.json`, and category names must match across all files.

## Design System

- Slate/gray palette (`#0f172a`, `#64748b`, `#e2e8f0`); status colors green/blue/yellow/red.
- Charts are hand-written SVG; layout is CSS Grid. No chart library.
- No emojis in UI.
