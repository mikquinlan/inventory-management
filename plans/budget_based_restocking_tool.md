# Restocking Tab

## Context

The app surfaces demand forecasts (`/demand`) but gives no way to act on them. Procurement users must eyeball the forecast table and place orders elsewhere. This adds a **Restocking** tab where the user sets an available budget with a slider, gets a budget-constrained restock recommendation derived from the demand forecast, adjusts quantities, and submits the order. Submitted orders then appear in the **Orders** tab under a new "Submitted Orders" section that shows supplier lead time and delivery ETA.

### Findings from exploration

- **No POST endpoints exist yet.** `server/main.py` is GET-only. `client/src/api.js` already declares `createTask`, `createPurchaseOrder`, `getTasks`, etc. against `/api/tasks` and `/api/purchase-orders` — **those routes do not exist in `main.py` and 404 today**. Do not model new work on them; `App.vue:89` swallows the error. `server/data/purchase_orders.json` is an empty array.
- **Forecast data has no cost.** `server/data/demand_forecasts.json` (9 rows) carries only demand numbers. 8 of its 9 SKUs (`WDG-001`, `BRG-102`, `GSK-203`, `MTR-304`, `FLT-405`, `VLV-506`, `SNR-420`, `CTL-330`) are **absent from `inventory.json`** — only `PSU-501` matches. So cost cannot be joined from inventory; it must be added to the forecast rows.
- Shared helpers to reuse: `apply_filters` / `filter_by_month` (`server/main.py:17,33`), `getCurrentFilters()` (`client/src/composables/useFilters.js:27`, maps `selectedLocation`→`warehouse`, `selectedPeriod`→`month`), `formatCurrency(amount, currentCurrency)` (`client/src/utils/currency.js`), `useI18n()` `t()` (`client/src/composables/useI18n.js`).
- Nav lives in `client/src/App.vue:9-28`; routes are declared inline in `client/src/main.js`. Global styles (`.card`, `.stat-card`, `.badge`, `table`) are in `App.vue`'s unscoped `<style>` — reuse them, keep new component styles `scoped`.

## Decisions (confirmed with user)

1. Cost/supplier/lead-time added as fields on `demand_forecasts.json` rows; new Pydantic fields are `Optional` so `Demand.vue` is untouched.
2. Submitted orders stored in a backend **module-level in-memory list** (matches existing mock-data pattern; resets on server restart).
3. Recommendation = greedy by demand shortfall, with **per-row editable quantities** and live over-budget blocking.
4. New top-nav tab `/restocking`; Orders tab gets a "Submitted Orders" card **above** the existing "All Orders" table.

---

## Implementation

### 1. Data — `server/data/demand_forecasts.json`

Add three fields to each of the 9 rows: `unit_cost` (float), `supplier` (string), `lead_time_days` (int). Keep `PSU-501` at `18.99` to match its `inventory.json` row. Suggested values (total full-restock ≈ $76K, which sets the slider range):

| sku     | unit_cost | lead_time_days |
| ------- | --------- | -------------- |
| WDG-001 | 12.50     | 14             |
| BRG-102 | 34.75     | 21             |
| GSK-203 | 8.25      | 10             |
| MTR-304 | 289.00    | 45             |
| FLT-405 | 15.40     | 7              |
| VLV-506 | 62.00     | 30             |
| PSU-501 | 18.99     | 12             |
| SNR-420 | 45.50     | 18             |
| CTL-330 | 156.00    | 35             |

Supplier names: invent plausible ones consistent in tone with `orders.json` customers (e.g. "Precision Parts Co", "Nordic Bearing Works").

### 2. Backend — `server/main.py`

- Extend `DemandForecast` with `unit_cost: Optional[float] = None`, `supplier: Optional[str] = None`, `lead_time_days: Optional[int] = None`.
- New models: `RestockRecommendation`, `SubmittedOrderLine`, `SubmittedOrder`, `CreateRestockOrderRequest`.
- Module-level `submitted_orders: list = []` (declare in `main.py`, not `mock_data.py` — it is runtime state, not loaded data).
- `GET /api/restocking/recommendations?budget=<float>` → `List[RestockRecommendation]`:
  - Candidate set = all forecasts with a `unit_cost`.
  - `recommended_quantity = forecasted_demand` (cover next period in full).
  - `shortfall = forecasted_demand - current_demand`; sort by `shortfall` descending (decreasing-trend items sort last naturally).
  - Greedy: walk sorted list, include a row at full quantity if `line_cost <= remaining budget`; else include it with `remaining // unit_cost` if that is ≥ 1; else mark `selected: false, recommended_quantity: 0`. Return **all** candidates with a `selected` flag so the UI can show what did not fit.
  - Each row returns `item_sku, item_name, unit_cost, supplier, lead_time_days, current_demand, forecasted_demand, shortfall, trend, recommended_quantity, line_cost, selected`.
  - Guard `budget` ≤ 0 → all rows `selected: false`, quantity 0.
- `POST /api/restocking/orders` → `SubmittedOrder` (201):
  - Body: `{ budget: float, items: [{ item_sku, item_name, quantity, unit_cost, supplier, lead_time_days }] }`.
  - Validate: non-empty `items`, every `quantity >= 1`, `total <= budget` → else `HTTPException(400, ...)`.
  - Generate `order_number` as `RST-2025-%04d` from `len(submitted_orders) + 1`; `submitted_date = datetime.now().isoformat(timespec='seconds')`; `lead_time_days = max(line lead times)`; `expected_delivery = submitted_date + lead_time_days`; `status = "Submitted"`; `total_value = sum(qty * unit_cost)`. Append and return.
- `GET /api/restocking/orders` → `List[SubmittedOrder]`, newest first.

Note the app-wide filter convention (`'all'` means no filter) does not apply here — restocking has no warehouse/category dimension, since forecast rows carry neither. Do **not** wire `getCurrentFilters()` into these calls.

### 3. API client — `client/src/api.js`

Add `getRestockRecommendations(budget)`, `createRestockOrder(payload)`, `getSubmittedOrders()`, following the existing axios + `URLSearchParams` style. Do not touch the pre-existing dead `tasks`/`purchase-orders` methods.

### 4. New view — `client/src/views/Restocking.vue`

**Delegate this file to the `vue-expert` subagent** (mandatory per CLAUDE.md for new `.vue` files).

- Composition API, `setup()`, `loading`/`error`/data refs per `client/CLAUDE.md`.
- Budget slider: `<input type="range">`, min `0`, max `100000`, step `1000`, default `50000`. Live value rendered via `formatCurrency(budget, currentCurrency)`.
- Debounce the slider (~300 ms `watch`) before calling `api.getRestockRecommendations`.
- Recommendation table: SKU, item name, supplier, trend badge (reuse global `.badge.increasing/.stable/.decreasing`), current vs forecasted demand, unit cost, editable quantity `<input type="number" min="0">`, line total. `:key="row.item_sku"` — never index (Gotcha 1).
- Stat cards above the table (reuse global `.stats-grid` / `.stat-card`): Budget, Allocated, Remaining, Items Selected. Remaining turns `.danger` when negative.
- "Place Order" button: disabled when nothing selected or total > budget. On success show a confirmation with the generated order number and clear the edits.
- All money through `formatCurrency`, never a hardcoded `$`. All labels through `t('restocking.*')`. No emojis.

### 5. Orders tab — `client/src/views/Orders.vue`

**Also delegate to `vue-expert`** (significant modification).

- Load submitted orders alongside existing orders in `loadOrders()` via `Promise.all`.
- Render a new "Submitted Orders ({n})" `.card` **above** the existing "All Orders" card, hidden with `v-if="submittedOrders.length"`.
- Columns: Order Number, Supplier(s), Items (reuse the existing `<details>` dropdown pattern at `Orders.vue:52-62`), Status badge (`Submitted` → `.badge.info`), Submitted Date, Lead Time (`{n} days`), Expected Delivery, Total Value.
- Reuse the existing `formatDate` helper; pass only backend-generated ISO dates, and keep the date-validation idiom if extending it (Gotcha 2).

### 6. Routing & nav

- `client/src/main.js`: import `Restocking` and add `{ path: '/restocking', component: Restocking }`.
- `client/src/App.vue`: add `<router-link to="/restocking">{{ t('nav.restocking') }}</router-link>` after the Demand Forecast link.

### 7. i18n — `client/src/locales/en.js` and `ja.js`

Add `nav.restocking` and a `restocking: { ... }` block (title, description, budget, allocated, remaining, itemsSelected, placeOrder, orderPlaced, overBudget, table.*, noRecommendations) plus `orders.submittedOrders`, `orders.table.leadTime`, `orders.table.submittedDate`, `orders.leadTimeDays`, and `status.submitted`. Both locales — English falls back automatically but Japanese should be filled in properly, matching the existing translation style.

### 8. Tests — `tests/backend/test_restocking.py`

Use the **`backend-api-test` skill** (mandatory per CLAUDE.md) and the existing `client` fixture from `tests/conftest.py`.

Cover: recommendations return 200 and a list; total `line_cost` of selected rows never exceeds budget; `budget=0` selects nothing; every row exposes the new cost/supplier/lead-time fields; POST creates an order and returns `order_number`/`expected_delivery`/`total_value`; POST over budget → 400; POST with empty items → 400; GET submitted orders includes the created one, newest first; existing `/api/demand` still returns 200 with the new optional fields present.

---

## Verification

1. `./scripts/start.sh` (backend :8001, frontend :3000).
2. Backend tests:
   ```bash
   cd tests && uv run --project ../server pytest -v
   ```
   Existing suite (40 tests) must still pass; `/api/demand` is the regression risk if the Pydantic model and JSON drift apart.
3. Spot-check the API:
   ```bash
   curl 'http://localhost:8001/api/restocking/recommendations?budget=30000'
   ```
   Confirm selected line costs sum ≤ 30000 and unselected rows come back with quantity 0.
4. Browser via **Playwright MCP** (`mcp__playwright__*`) against `http://localhost:3000`:
   - Open `/restocking`; drag the slider low and high — recommendation set and stat cards change.
   - Edit a quantity above budget; confirm Remaining goes negative/red and "Place Order" disables.
   - Reset, click "Place Order", confirm the success message with an `RST-2025-0001` order number.
   - Navigate to `/orders`; confirm the "Submitted Orders" card appears above "All Orders" with lead time and expected delivery.
   - Switch locale to 日本語; confirm labels translate and amounts render in ¥ (no stray `$`).
5. `code-reviewer` subagent pass over the diff before finishing.
