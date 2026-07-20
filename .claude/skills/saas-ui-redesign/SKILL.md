---
name: saas-ui-redesign
description: Redesign the Vue 3 client into a modern SaaS-style interface — vertical left sidebar navigation replacing the top nav bar, a design-token system, consistent spacing, and polished cards/tables/forms. Use when asked to modernize, restyle, or redesign the UI, move navigation to a sidebar, or make the app look like a professional SaaS product.
---

# SaaS UI Redesign

Converts this app's top-nav layout into a sidebar-driven SaaS shell without changing any data flow, API call, or business logic.

## Rules

1. **Delegate every `.vue` write to `vue-expert`** (project CLAUDE.md mandates this). This skill is the plan; vue-expert does the edits.
2. **Layout and styling only.** Do not touch `api.js`, composables' logic, or backend. Existing `setup()` blocks, refs, computed, and props stay as-is.
3. **No new dependencies.** No Tailwind, no UI kit, no icon package. Hand-written CSS and inline SVG only — matches the existing "hand-written SVG charts, no chart library" convention.
4. **i18n is not optional.** Every nav label and new visible string goes through `t('...')` with keys added to **both** `client/src/locales/en.js` and `ja.js`. Never hardcode English.
5. **No emojis in UI** (design system rule). Icons are inline SVG.
6. **Money renders through `formatCurrency(amount, currentCurrency)`** — never a hardcoded `$`.
7. Preserve `v-for` stable-ID keys; do not "clean up" to indexes.

## Current state (verify before assuming — files drift)

- `client/src/App.vue` — holds `<header class="top-nav">` with the 7 `router-link`s, plus the **global unscoped `<style>` block** (~line 167+) that every view depends on: `.page-header`, `.stats-grid`, `.stat-card`, `.card`, `.card-header`, `.card-title`, `table/th/td`, `.badge.*`, `.loading`, `.error`.
- `client/src/components/FilterBar.vue` — full-width bar rendered between nav and `<main>`.
- Views: `Dashboard`, `Inventory`, `Orders`, `Spending`, `Demand`, `Restocking`, `Reports`. (`Backlog.vue` is dead code — no route. Skip it.)
- Routes are declared inline in `client/src/main.js` — read it for the authoritative path list rather than trusting the nav template.
- Palette: slate/gray `#0f172a` / `#64748b` / `#e2e8f0`, accent `#2563eb`, status green/blue/yellow/red.

**Critical:** those global class names are used across all views. Restyle them in place; renaming a global class silently breaks every view that uses it.

## Step 1 — Design tokens

Add a `:root` block at the top of App.vue's global `<style>`, then express new CSS in terms of it. Refactor existing rules to tokens opportunistically, not in a big-bang rewrite.

```css
:root {
  /* spacing — 4px scale, use these instead of ad-hoc rem values */
  --sp-1: 0.25rem; --sp-2: 0.5rem;  --sp-3: 0.75rem; --sp-4: 1rem;
  --sp-5: 1.5rem;  --sp-6: 2rem;    --sp-8: 3rem;

  /* surfaces */
  --bg-app: #f8fafc; --bg-surface: #ffffff; --bg-subtle: #f1f5f9;
  --border: #e2e8f0; --border-strong: #cbd5e1;

  /* text */
  --text-primary: #0f172a; --text-secondary: #475569; --text-muted: #64748b;

  /* accent + status */
  --accent: #2563eb; --accent-subtle: #eff6ff;
  --success: #059669; --warning: #ea580c; --danger: #dc2626;

  /* shape */
  --radius-sm: 6px; --radius: 10px; --radius-lg: 14px;
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow: 0 4px 12px rgba(15, 23, 42, 0.06);

  /* sidebar */
  --sidebar-w: 248px; --sidebar-w-collapsed: 68px;
}
```

Spacing discipline: **only** token values. Vertical rhythm — section gap `--sp-5`, card padding `--sp-5`, intra-card gap `--sp-4`, label-to-value `--sp-2`.

## Step 2 — Sidebar shell

Replace the `.top-nav` header with a two-column grid in `App.vue`:

```
.app-shell  → display: grid; grid-template-columns: var(--sidebar-w) 1fr; min-height: 100vh;
  aside.sidebar   → position: sticky; top: 0; height: 100vh; background: var(--bg-surface);
                    border-right: 1px solid var(--border); display: flex; flex-direction: column;
  .app-main       → display: flex; flex-direction: column; min-width: 0;  /* min-width:0 or wide
                       tables blow out the grid column instead of scrolling */
    header.topbar → page title + LanguageSwitcher + ProfileMenu, sticky, h ~64px
    FilterBar
    main.main-content → padding: var(--sp-5) var(--sp-6); flex: 1;
```

Sidebar contents top→bottom:
1. **Brand** — `t('nav.companyName')` + `t('nav.subtitle')`, padding `--sp-5 --sp-4`, bottom border.
2. **Nav list** — `<nav><ul>` of `router-link`s. Each item: 20px inline SVG icon + label, `padding: var(--sp-2) var(--sp-3)`, `gap: var(--sp-3)`, `border-radius: var(--radius-sm)`, `--text-muted`.
   - hover: `background: var(--bg-subtle); color: var(--text-primary)`
   - active: `background: var(--accent-subtle); color: var(--accent); font-weight: 600`, plus a 3px `--accent` left rail via `::before`.
   - Use `router-link`'s own `.router-link-active` where the path is unambiguous, but keep the existing explicit `:class="{ active: $route.path === '...' }"` pattern for `/` — otherwise the root link stays active on every route.
   - Optional: group with small uppercase section labels (e.g. Operations / Planning / Insights) if the item count justifies it.
3. **Spacer** (`margin-top: auto`) then a collapse toggle.

**Collapse** — `const sidebarCollapsed = ref(false)`, persist to `localStorage` (key `sidebar-collapsed`, same convention as `useI18n`'s `app-locale`). Collapsed: shell column becomes `--sidebar-w-collapsed`, labels hidden, icons centered, `title` attribute carries the label.

**Move `LanguageSwitcher` and `ProfileMenu` into the topbar**, right-aligned, `gap: var(--sp-3)`. Their emitted events (`show-profile-details`, `show-tasks`) and the two modals stay wired exactly as they are.

Delete `.nav-container`, `.nav-tabs`, and the `.max-width: 1600px` centering — a sidebar shell is full-bleed; the content column caps itself instead.

## Step 3 — Polish the shared primitives

Restyle in place, keeping class names:

- `.card` — `border-radius: var(--radius)`, `box-shadow: var(--shadow-sm)`, padding `var(--sp-5)`, `margin-bottom: var(--sp-5)`.
- `.stat-card` — same shell; label `--text-muted` uppercase `0.75rem`, value `2rem/700`, optional delta line. Keep `.warning/.success/.danger/.info` modifiers.
- `.stats-grid` — `gap: var(--sp-4)`, `minmax(240px, 1fr)`.
- Tables — sticky `thead` inside `.table-container` (`overflow: auto; max-height` where a view has long lists), zebra-free with `1px solid #f1f5f9` row borders, hover `--bg-subtle`, first/last cell padding `var(--sp-4)`.
- `.badge` — `--radius-sm`, `0.6875rem`, keep every existing modifier (`success warning danger info increasing decreasing stable high medium low`). Missing one breaks a view.
- Add `.btn` / `.btn-primary` / `.btn-ghost` and `.input` / `.select` only if views currently style buttons/inputs ad hoc — check first, then consolidate.
- `.loading` / `.error` — keep names, soften to tokens; a skeleton shimmer for `.loading` is a nice-to-have, not required.

## Step 4 — Responsive

- `>1280px`: sidebar expanded.
- `768–1280px`: force collapsed (icons only).
- `<768px`: sidebar off-canvas — `position: fixed; transform: translateX(-100%)`, hamburger in the topbar toggles it, backdrop overlay closes it. Grid becomes single-column.

Close the mobile drawer on route change (`watch(() => route.path, ...)`) or it stays open over the new page.

## Step 5 — Verify

Servers must be up (`./scripts/start.sh`; frontend :3000, backend :8001 — no Vite proxy, so an unreachable backend means empty views, not a layout bug).

Use **Playwright MCP** (`mcp__playwright__*`, project rule):
1. Visit every route from `main.js`. Screenshot each at 1440px.
2. Re-check at 1024px and 390px widths.
3. `browser_console_messages` — must be free of Vue warnings; a missing-key or undefined-component warning here is usually a half-finished nav edit.
4. Toggle locale to `ja` and confirm no untranslated key strings (`nav.someKey` rendering literally) and no sidebar label overflow.
5. Toggle sidebar collapse, reload, confirm state persisted.

Then run `code-reviewer` on the diff.

Backend tests are unaffected, but they're cheap — `cd tests && uv run --project ../server pytest -v` confirms nothing bled across.

## Scope discipline

Redesigns sprawl. Ship in this order and let the user review between phases:

1. Tokens + sidebar shell + topbar (App.vue only) — app is fully usable after this alone.
2. Shared primitives (still App.vue global styles) — lifts every view for free.
3. Per-view spacing/hierarchy passes, one view per delegation.

Never rewrite a view's script block "while in there." If a view needs logic changes to look right, surface it to the user instead of doing it silently.
