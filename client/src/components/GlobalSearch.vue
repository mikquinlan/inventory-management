<template>
  <div class="global-search" ref="rootRef" :class="{ expanded }">
    <button
      type="button"
      class="search-toggle"
      @click="handleToggleClick"
      :aria-label="t('search.placeholder')"
    >
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="8" cy="8" r="5.5"/>
        <path d="M12.2 12.2L16 16" stroke-linecap="round"/>
      </svg>
    </button>

    <div class="search-field">
      <svg class="search-field-icon" width="16" height="16" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="8" cy="8" r="5.5"/>
        <path d="M12.2 12.2L16 16" stroke-linecap="round"/>
      </svg>
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        class="search-input"
        :placeholder="t('search.placeholder')"
        :aria-label="t('search.placeholder')"
        role="combobox"
        aria-autocomplete="list"
        :aria-expanded="showPanel"
        @input="onQueryInput"
        @keydown="onKeydown"
        @focus="onFocus"
      />
    </div>

    <div v-if="showPanel" class="search-panel">
      <ul v-if="results.length" class="search-results" role="listbox">
        <li
          v-for="(item, index) in results"
          :key="item.sku"
          class="search-result"
          role="option"
          :aria-selected="index === highlightedIndex"
          :class="{ highlighted: index === highlightedIndex }"
          @mousedown.prevent="selectResult(item)"
          @mouseenter="highlightedIndex = index"
        >
          <span class="result-sku">{{ item.sku }}</span>
          <span class="result-name">{{ item.name }}</span>
        </li>
      </ul>
      <div v-else class="search-empty">{{ t('search.noResults') }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import { api } from '../api'

const { t } = useI18n()
const router = useRouter()

const rootRef = ref(null)
const inputRef = ref(null)

const query = ref('')
const debouncedQuery = ref('')
const expanded = ref(false)
const panelOpen = ref(false)
const highlightedIndex = ref(-1)

const inventoryCache = ref(null)
const cacheLoading = ref(false)
const cacheFetchedAt = ref(0)
const CACHE_TTL_MS = 60000

let debounceTimer = null

const results = computed(() => {
  const q = debouncedQuery.value.trim().toLowerCase()
  if (!q || !inventoryCache.value) return []
  return inventoryCache.value
    .filter(item =>
      (item.sku && item.sku.toLowerCase().includes(q)) ||
      (item.name && item.name.toLowerCase().includes(q))
    )
    .slice(0, 8)
})

const showPanel = computed(() => panelOpen.value && debouncedQuery.value.trim().length > 0)

const ensureCacheLoaded = async () => {
  const isStale = inventoryCache.value === null || (Date.now() - cacheFetchedAt.value) > CACHE_TTL_MS
  if (!isStale || cacheLoading.value) return
  cacheLoading.value = true
  try {
    inventoryCache.value = await api.getInventory({})
    cacheFetchedAt.value = Date.now()
  } catch (err) {
    console.error('GlobalSearch: failed to load inventory', err)
    if (inventoryCache.value === null) inventoryCache.value = []
  } finally {
    cacheLoading.value = false
  }
}

const closePanel = () => {
  panelOpen.value = false
  highlightedIndex.value = -1
}

const onFocus = () => {
  expanded.value = true
  ensureCacheLoaded()
  if (query.value.trim().length > 0) {
    panelOpen.value = true
  }
}

const onQueryInput = () => {
  ensureCacheLoaded()
  panelOpen.value = true
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    debouncedQuery.value = query.value
    highlightedIndex.value = -1
  }, 250)
}

const onKeydown = (event) => {
  if (event.key === 'Escape') {
    closePanel()
    inputRef.value && inputRef.value.blur()
  } else if (event.key === 'ArrowDown') {
    if (!showPanel.value || results.value.length === 0) return
    event.preventDefault()
    highlightedIndex.value = (highlightedIndex.value + 1) % results.value.length
  } else if (event.key === 'ArrowUp') {
    if (!showPanel.value || results.value.length === 0) return
    event.preventDefault()
    highlightedIndex.value = (highlightedIndex.value - 1 + results.value.length) % results.value.length
  } else if (event.key === 'Enter') {
    if (!showPanel.value || results.value.length === 0) return
    const item = results.value[highlightedIndex.value] ?? results.value[0]
    if (item) {
      event.preventDefault()
      selectResult(item)
    }
  }
}

const selectResult = (item) => {
  closePanel()
  query.value = ''
  debouncedQuery.value = ''
  expanded.value = false
  router.push('/inventory')
}

const handleToggleClick = () => {
  expanded.value = true
  requestAnimationFrame(() => {
    inputRef.value && inputRef.value.focus()
  })
}

const handleOutsideClick = (event) => {
  if (rootRef.value && !rootRef.value.contains(event.target)) {
    closePanel()
    expanded.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<style scoped>
.global-search {
  position: relative;
  display: flex;
  align-items: center;
  width: 320px;
}

.search-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
}

.search-toggle:hover {
  background: var(--bg-subtle);
  border-color: var(--border-strong);
}

.search-field {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  width: 100%;
  padding: var(--sp-2) var(--sp-3);
  background: var(--bg-subtle);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  transition: border-color 0.15s ease, background 0.15s ease;
}

.search-field:focus-within {
  background: var(--bg-surface);
  border-color: var(--accent);
}

.search-field-icon {
  flex-shrink: 0;
  color: var(--text-muted);
}

.search-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-family: inherit;
  font-size: 0.875rem;
  color: var(--text-primary);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-panel {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  max-height: 320px;
  overflow-y: auto;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow);
  z-index: 160;
}

.search-results {
  list-style: none;
}

.search-result {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sp-3);
  padding: var(--sp-2) var(--sp-3);
  cursor: pointer;
  font-size: 0.8125rem;
}

.search-result:hover,
.search-result.highlighted {
  background: var(--bg-subtle);
}

.result-sku {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-family: 'SFMono-Regular', Consolas, monospace;
}

.result-name {
  flex: 1;
  min-width: 0;
  text-align: right;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.search-empty {
  padding: var(--sp-4);
  text-align: center;
  color: var(--text-muted);
  font-size: 0.8125rem;
}

@media (max-width: 1024px) {
  .global-search {
    width: auto;
  }

  .search-toggle {
    display: flex;
  }

  .search-field {
    display: none;
  }

  .global-search.expanded .search-field {
    display: flex;
    position: absolute;
    top: 0;
    right: 0;
    width: 280px;
    background: var(--bg-surface);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    z-index: 150;
  }
}
</style>
