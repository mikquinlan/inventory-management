---
name: vue-optimize
description: Analyze Vue 3 component structure and report performance and code-reuse optimizations — oversized components, duplicated modal/fetch/watch boilerplate, missed computed memoization, unstable v-for keys, extractable composables. Use when asked to audit, optimize, refactor, or clean up Vue components, reduce duplication in the client, or improve frontend rendering performance.
---

# Vue Component Optimization Audit

Analyzes `client/src/` and produces a **prioritized report**. Refactors only when the user approves a specific finding.

## Rules

1. **Audit first, edit never (by default).** Output is a report. Only apply a fix after the user picks findings.
2. **Any `.vue` write goes to `vue-expert`** — project CLAUDE.md mandates it. This skill diagnoses; vue-expert edits.
3. **No new dependencies.** No Pinia, no VueUse, no UI kit. Extraction targets are plain composables and local components.
4. **Behavior-preserving only.** Do not change API params, filter semantics, or rendered numbers. If a fix would alter output, report it as a bug, not an optimization.
5. **Respect house conventions**: `formatCurrency(amount, currentCurrency)` for money, `t('...')` for strings in **both** `locales/en.js` and `ja.js`, `getCurrentFilters()` for filter translation, no emojis, scoped styles except `App.vue`'s global block.

## Step 1 — Measure

```bash
cd client/src
wc -l views/*.vue components/*.vue composables/*.js | sort -rn
```

Flag any `.vue` over **400 lines** as a split candidate. Record the numbers — the report leads with them.

Then map each file's shape: template size vs `setup()` size, number of `ref`s, number of `computed`s, and whether it owns data-fetching.

## Step 2 — Reuse scan

Run these and read the hits, not just the counts:

```bash
# duplicated fetch/loading/error scaffolding
grep -n "const loading = ref\|const error = ref" views/*.vue components/*.vue

# duplicated filter-watch wiring
grep -n "watch(\[" views/*.vue

# modal shell duplication (overlay, close-on-escape, backdrop click, header)
grep -n "modal-overlay\|@keydown.esc\|class=\"modal" components/*.vue

# repeated formatting helpers defined per-component instead of imported
grep -n "const format\|function format" views/*.vue components/*.vue

# repeated inline SVG chart math
grep -n "polyline\|<path d=\|viewBox" views/*.vue
```

Known duplication in this repo (re-verify — files drift):

| Pattern | Where | Extract to |
|---|---|---|
| `loading`/`error` refs + try/catch/finally fetch block | all 6 data views | `composables/useApiData.js` returning `{ data, loading, error, reload }` |
| `watch([selectedLocation, selectedCategory, ...], loadData)` | Dashboard, Orders, Inventory, Demand, Spending | fold the watch into `useApiData` so callers pass a loader and a dep list once |
| Modal overlay + backdrop + close button + escape key | 6 `*Modal.vue` files | `components/BaseModal.vue` with `<slot name="header">` / default slot; keeps each modal's body intact |
| Per-component number/percent formatters | scattered | `utils/` alongside `currency.js` |

Extraction is only justified when **3+ call sites** share the shape. Two sites is a coincidence; say so and move on.

## Step 3 — Performance scan

Check each, cite `file:line`, and say what the user would actually observe:

1. **Unstable `v-for` keys** — `:key="index"` breaks Vue's patch reuse and corrupts component state on reorder. Known offenders live in `views/Reports.vue` (quarterly and monthly rows/bars). Replace with `q.quarter` / `month.month`.
2. **Work in the template that should be `computed`** — expressions like `((summary.total_orders_value / revenueGoal - 1) * 100).toFixed(1)` re-evaluate on every render of that component. Heavy ones (loops, `.filter().reduce()`, date parsing, chart-point math) must become `computed`. Cheap arithmetic on a single value is fine — don't churn the diff for it.
3. **Function calls in templates over lists** — a helper invoked inside `v-for` runs once per row per render. Precompute a derived array in one `computed` instead.
4. **`v-if` + `v-for` on the same element** — filter in a `computed`, not in the template.
5. **Large always-rendered subtrees** — modals and detail panels hidden with `v-show`/CSS still mount and re-render. Gate with `v-if` when the content is expensive.
6. **Missing `v-once` / static hoisting opportunities** — only for genuinely constant markup blocks; low value, report last.
7. **Watchers that refetch more than needed** — a watcher on the whole filter set that reloads an endpoint ignoring one of those filters is a wasted round-trip. `/api/inventory` has **no month filter** (see CLAUDE.md gotcha 3), so a `selectedPeriod` change must not trigger an inventory refetch.
8. **Module-scope singleton composables** (`useFilters`, `useI18n`, `useAuth`) — state is shared process-wide by design. Never "fix" this by moving refs inside the exported function; that silently desynchronizes every consumer.

## Step 4 — Report

Group findings under **Performance**, **Reuse**, **Structure**. One line each:

```
client/src/views/Reports.vue:28  [perf][high]  :key="index" on quarterlyData — row state misbinds on reorder. Use :key="q.quarter".
client/src/views/Dashboard.vue:906 [structure][med] 906 lines. Split KPI grid, summary table, and SVG charts into components under views/dashboard/.
```

Severity:
- **high** — measurably wrong rendering or a repeated network call
- **med** — real duplication (3+ sites) or a file over 400 lines
- **low** — micro-optimizations, naming, hoisting

Close with a **recommended order**: cheap correctness fixes (keys, redundant refetches) first, extractions second, file splits last — splits are the largest diff and the highest regression risk.

## Step 5 — Apply (only if asked)

Per approved finding:
1. Hand `vue-expert` the file, the exact line, the problem, and the intended shape.
2. One finding per delegation. No bundling.
3. After the edit, verify in the browser with Playwright MCP against `http://localhost:3000` (backend must be up on `:8001` — `./scripts/start.sh`). Confirm the affected view still renders the same values.
4. There is no frontend test runner. Visual and console verification is the only gate — check `browser_console_messages` for new warnings.
