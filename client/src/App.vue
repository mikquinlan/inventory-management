<template>
  <div class="app-shell" :class="{ collapsed: sidebarCollapsed }">
    <aside
      ref="sidebarRef"
      class="sidebar"
      :class="{ collapsed: sidebarCollapsed, open: mobileSidebarOpen }"
      tabindex="-1"
    >
      <div class="sidebar-brand">
        <div class="brand-mark">{{ brandInitial }}</div>
        <div class="brand-text">
          <div class="brand-name">{{ t("nav.companyName") }}</div>
          <div class="brand-subtitle">{{ t("nav.subtitle") }}</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div
          v-for="section in navSections"
          :key="section.key"
          class="nav-section"
        >
          <div class="nav-section-label">{{ t(section.labelKey) }}</div>
          <ul>
            <li v-for="item in section.items" :key="item.path">
              <router-link
                :to="item.path"
                :class="{ active: $route.path === item.path }"
                :aria-current="$route.path === item.path ? 'page' : undefined"
                :title="sidebarCollapsed ? t(item.labelKey) : null"
              >
                <span class="nav-icon" aria-hidden="true">
                  <svg
                    v-if="item.icon === 'home'"
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  >
                    <path
                      d="M3.5 9.5L10 4l6.5 5.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M5.5 8.5V16a1 1 0 001 1H8.5v-4.5h3V17H13.5a1 1 0 001-1V8.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  <svg
                    v-else-if="item.icon === 'box'"
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  >
                    <path
                      d="M10 3l6 3.2v7.6L10 17l-6-3.2V6.2L10 3z"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M4 6.2L10 9.4l6-3.2M10 9.4V17"
                      stroke-linejoin="round"
                    />
                  </svg>
                  <svg
                    v-else-if="item.icon === 'clipboard'"
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  >
                    <rect x="5" y="4" width="10" height="13" rx="1.5" />
                    <path
                      d="M8 4V3a1 1 0 011-1h2a1 1 0 011 1v1"
                      stroke-linecap="round"
                    />
                    <path d="M7.5 9.5h5M7.5 12.5h5" stroke-linecap="round" />
                  </svg>
                  <svg
                    v-else-if="item.icon === 'trending'"
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  >
                    <path
                      d="M3.5 13.5l4.5-4.5 3 3 5.5-6"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M12.5 6h4v4"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  <svg
                    v-else-if="item.icon === 'refresh'"
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  >
                    <path
                      d="M4.5 10a5.5 5.5 0 019.4-3.9M15.5 10a5.5 5.5 0 01-9.4 3.9"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M13.5 3.5v3h-3M6.5 16.5v-3h3"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  <svg
                    v-else-if="item.icon === 'wallet'"
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  >
                    <rect x="2.5" y="5.5" width="15" height="10.5" rx="1.5" />
                    <path d="M2.5 8.5h15" stroke-linecap="round" />
                    <circle
                      cx="14"
                      cy="12"
                      r="1"
                      fill="currentColor"
                      stroke="none"
                    />
                  </svg>
                  <svg
                    v-else-if="item.icon === 'chart'"
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  >
                    <path
                      d="M4 16.5V10M9 16.5V6M14 16.5v-4M18 16.5V3"
                      stroke-linecap="round"
                    />
                  </svg>
                </span>
                <span class="nav-label">{{ t(item.labelKey) }}</span>
              </router-link>
            </li>
          </ul>
        </div>
      </nav>

      <div class="sidebar-footer">
        <button
          class="sidebar-toggle"
          type="button"
          @click="toggleSidebarCollapsed"
          :aria-label="t(sidebarCollapsed ? 'nav.expand' : 'nav.collapse')"
          :aria-expanded="!sidebarCollapsed"
        >
          <svg
            class="toggle-icon"
            :class="{ rotated: sidebarCollapsed }"
            width="18"
            height="18"
            viewBox="0 0 18 18"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path
              d="M11 4l-5 5 5 5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          <span class="nav-label">{{ t("nav.collapse") }}</span>
        </button>
      </div>
    </aside>

    <div
      v-if="mobileSidebarOpen"
      class="sidebar-backdrop"
      @click="closeMobileSidebar"
    ></div>

    <div class="app-main">
      <header class="topbar">
        <div class="topbar-left">
          <button
            ref="mobileMenuBtnRef"
            class="mobile-menu-btn"
            type="button"
            @click="openMobileSidebar"
            :aria-label="t('nav.menu')"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <path d="M3 5.5h14M3 10h14M3 14.5h14" stroke-linecap="round" />
            </svg>
          </button>
          <nav class="breadcrumbs" aria-label="Breadcrumb">
            <span class="crumb muted">{{ t("nav.companyName") }}</span>
            <span class="crumb-sep">/</span>
            <span class="crumb current">{{ currentPageLabel }}</span>
          </nav>
        </div>

        <div class="topbar-center">
          <GlobalSearch />
        </div>

        <div class="topbar-right">
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="showProfileDetails = true"
            @show-tasks="showTasks = true"
          />
        </div>
      </header>

      <FilterBar />

      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import {
  ref,
  onMounted,
  onBeforeUnmount,
  computed,
  watch,
  nextTick,
} from "vue";
import { useRoute } from "vue-router";
import { api } from "./api";
import { useAuth } from "./composables/useAuth";
import { useI18n } from "./composables/useI18n";
import FilterBar from "./components/FilterBar.vue";
import ProfileMenu from "./components/ProfileMenu.vue";
import ProfileDetailsModal from "./components/ProfileDetailsModal.vue";
import TasksModal from "./components/TasksModal.vue";
import LanguageSwitcher from "./components/LanguageSwitcher.vue";
import GlobalSearch from "./components/GlobalSearch.vue";

export default {
  name: "App",
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher,
    GlobalSearch,
  },
  setup() {
    const { currentUser } = useAuth();
    const { t } = useI18n();
    const route = useRoute();
    const showProfileDetails = ref(false);
    const showTasks = ref(false);
    const apiTasks = ref([]);

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value];
    });

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks();
      } catch (err) {
        console.error("Failed to load tasks:", err);
      }
    };

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData);
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask);
      } catch (err) {
        console.error("Failed to add task:", err);
      }
    };

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some((t) => t.id === taskId);

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(
            (t) => t.id === taskId,
          );
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1);
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId);
          apiTasks.value = apiTasks.value.filter((t) => t.id !== taskId);
        }
      } catch (err) {
        console.error("Failed to delete task:", err);
      }
    };

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find((t) => t.id === taskId);

        if (mockTask) {
          // Toggle mock task status
          mockTask.status =
            mockTask.status === "pending" ? "completed" : "pending";
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId);
          const index = apiTasks.value.findIndex((t) => t.id === taskId);
          if (index !== -1) {
            apiTasks.value[index] = updatedTask;
          }
        }
      } catch (err) {
        console.error("Failed to toggle task:", err);
      }
    };

    onMounted(loadTasks);

    // --- Sidebar navigation / layout ---
    const navSections = [
      {
        key: "operations",
        labelKey: "nav.sections.operations",
        items: [
          { path: "/", labelKey: "nav.overview", icon: "home" },
          { path: "/inventory", labelKey: "nav.inventory", icon: "box" },
          { path: "/orders", labelKey: "nav.orders", icon: "clipboard" },
        ],
      },
      {
        key: "planning",
        labelKey: "nav.sections.planning",
        items: [
          { path: "/demand", labelKey: "nav.demandForecast", icon: "trending" },
          { path: "/restocking", labelKey: "nav.restocking", icon: "refresh" },
        ],
      },
      {
        key: "insights",
        labelKey: "nav.sections.insights",
        items: [
          { path: "/spending", labelKey: "nav.finance", icon: "wallet" },
          { path: "/reports", labelKey: "nav.reports", icon: "chart" },
        ],
      },
    ];

    const routeLabelMap = {
      "/": "nav.overview",
      "/inventory": "nav.inventory",
      "/orders": "nav.orders",
      "/demand": "nav.demandForecast",
      "/restocking": "nav.restocking",
      "/spending": "nav.finance",
      "/reports": "nav.reports",
    };

    const currentPageLabel = computed(() =>
      t(routeLabelMap[route.path] || "nav.overview"),
    );
    const brandInitial = computed(
      () => (t("nav.companyName") || "").charAt(0) || "C",
    );

    const sidebarCollapsed = ref(
      localStorage.getItem("sidebar-collapsed") === "true",
    );
    const toggleSidebarCollapsed = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value;
      localStorage.setItem("sidebar-collapsed", String(sidebarCollapsed.value));
    };

    const mobileSidebarOpen = ref(false);
    const sidebarRef = ref(null);
    const mobileMenuBtnRef = ref(null);

    const openMobileSidebar = () => {
      mobileSidebarOpen.value = true;
    };

    const closeMobileSidebar = () => {
      if (!mobileSidebarOpen.value) return;
      mobileSidebarOpen.value = false;
      mobileMenuBtnRef.value && mobileMenuBtnRef.value.focus();
    };

    watch(
      () => route.path,
      () => {
        mobileSidebarOpen.value = false;
      },
    );

    watch(mobileSidebarOpen, (isOpen) => {
      if (isOpen) {
        nextTick(() => {
          sidebarRef.value && sidebarRef.value.focus();
        });
      }
    });

    const onGlobalKeydown = (event) => {
      if (event.key === "Escape" && mobileSidebarOpen.value) {
        closeMobileSidebar();
      }
    };

    onMounted(() => {
      document.addEventListener("keydown", onGlobalKeydown);
    });

    onBeforeUnmount(() => {
      document.removeEventListener("keydown", onGlobalKeydown);
    });

    return {
      t,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask,
      navSections,
      currentPageLabel,
      brandInitial,
      sidebarCollapsed,
      toggleSidebarCollapsed,
      mobileSidebarOpen,
      sidebarRef,
      mobileMenuBtnRef,
      openMobileSidebar,
      closeMobileSidebar,
    };
  },
};
</script>

<style>
:root {
  --sp-1: 0.25rem;
  --sp-2: 0.5rem;
  --sp-3: 0.75rem;
  --sp-4: 1rem;
  --sp-5: 1.5rem;
  --sp-6: 2rem;
  --sp-8: 3rem;

  --bg-app: #f8fafc;
  --bg-surface: #fff;
  --bg-subtle: #f1f5f9;

  --border: #e2e8f0;
  --border-strong: #cbd5e1;

  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #64748b;

  --accent: #4f46e5;
  --accent-subtle: #eef2ff;
  --accent-strong: #4338ca;

  --success: #059669;
  --warning: #ea580c;
  --danger: #dc2626;
  --info: #3b82f6;

  /* categorical chart series — distinct hues, not status colors */
  --chart-1: #4f46e5;
  --chart-2: #0ea5e9;
  --chart-3: #059669;
  --chart-4: #f59e0b;
  --chart-5: #db2777;

  --radius-sm: 6px;
  --radius: 10px;
  --radius-lg: 14px;

  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow: 0 4px 12px rgba(15, 23, 42, 0.06);

  --sidebar-w: 248px;
  --sidebar-w-collapsed: 68px;
  --topbar-h: 64px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family:
    "Inter",
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    Roboto,
    Oxygen,
    Ubuntu,
    Cantarell,
    sans-serif;
  background: var(--bg-app);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ---------- App shell ---------- */

.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr;
  min-height: 100vh;
}

.app-shell.collapsed {
  grid-template-columns: var(--sidebar-w-collapsed) 1fr;
}

/* ---------- Sidebar ---------- */

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  overflow-x: hidden;
  overflow-y: auto;
  z-index: 110;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-5) var(--sp-4);
  border-bottom: 1px solid var(--border);
}

.sidebar.collapsed .sidebar-brand {
  justify-content: center;
  padding: var(--sp-5) var(--sp-2);
}

.brand-mark {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: -0.02em;
}

.brand-text {
  min-width: 0;
}

.brand-name {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-nav {
  flex: 1;
  padding: var(--sp-4) var(--sp-3);
}

.nav-section + .nav-section {
  margin-top: var(--sp-5);
}

.nav-section-label {
  padding: 0 var(--sp-3);
  margin-bottom: var(--sp-2);
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}

.sidebar-nav ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--sp-1);
}

.sidebar-nav a {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-2) var(--sp-3);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}

.sidebar.collapsed .sidebar-nav a {
  justify-content: center;
}

.sidebar-nav a:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}

.sidebar-nav a.active {
  background: var(--accent-subtle);
  color: var(--accent);
  font-weight: 600;
}

.sidebar-nav a.active::before {
  content: "";
  position: absolute;
  left: calc(var(--sp-3) * -1);
  top: 0;
  bottom: 0;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--accent);
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar.collapsed .nav-label,
.sidebar.collapsed .nav-section-label,
.sidebar.collapsed .brand-text {
  display: none;
}

.sidebar-footer {
  margin-top: auto;
  padding: var(--sp-3);
  border-top: 1px solid var(--border);
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  width: 100%;
  padding: var(--sp-2) var(--sp-3);
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}

.sidebar.collapsed .sidebar-toggle {
  justify-content: center;
}

.sidebar-toggle:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}

.toggle-icon {
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

.sidebar-backdrop {
  display: none;
}

/* ---------- Main column ---------- */

.app-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  height: var(--topbar-h);
  display: flex;
  align-items: center;
  gap: var(--sp-4);
  padding: 0 var(--sp-6);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  min-width: 0;
}

.mobile-menu-btn {
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

.mobile-menu-btn:hover {
  background: var(--bg-subtle);
  border-color: var(--border-strong);
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  font-size: 0.875rem;
  min-width: 0;
  overflow: hidden;
}

.crumb {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.crumb.muted {
  color: var(--text-muted);
}

.crumb.current {
  color: var(--text-primary);
  font-weight: 600;
}

.crumb-sep {
  color: var(--border-strong);
}

.topbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
  min-width: 0;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  width: 100%;
  padding: var(--sp-5) var(--sp-6);
}

/* ---------- Shared primitives (used across all views) ---------- */

.page-header {
  margin-bottom: var(--sp-5);
}

.page-header h2 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--sp-1);
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--text-muted);
  font-size: 0.938rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--sp-4);
  margin-bottom: var(--sp-5);
}

.stat-card {
  background: var(--bg-surface);
  padding: var(--sp-5);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow);
}

.stat-label {
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--sp-2);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: var(--warning);
}

.stat-card.success .stat-value {
  color: var(--success);
}

.stat-card.danger .stat-value {
  color: var(--danger);
}

.stat-card.info .stat-value {
  color: var(--accent);
}

.card {
  background: var(--bg-surface);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  padding: var(--sp-5);
  margin-bottom: var(--sp-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--sp-4);
  padding-bottom: var(--sp-3);
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  position: sticky;
  top: 0;
  background: var(--bg-app);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  z-index: 1;
}

th {
  text-align: left;
  padding: var(--sp-3) var(--sp-4);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: var(--sp-3) var(--sp-4);
  border-top: 1px solid var(--bg-subtle);
  color: #334155;
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--bg-subtle);
}

.badge {
  display: inline-block;
  padding: 0.313rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success {
  background: #d1fae5;
  color: #065f46;
}

.badge.warning {
  background: #fed7aa;
  color: #92400e;
}

.badge.danger {
  background: #fecaca;
  color: #991b1b;
}

.badge.info {
  background: #dbeafe;
  color: #1e40af;
}

.badge.increasing {
  background: #d1fae5;
  color: #065f46;
}

.badge.decreasing {
  background: #fecaca;
  color: #991b1b;
}

.badge.stable {
  background: #e0e7ff;
  color: #3730a3;
}

.badge.high {
  background: #fecaca;
  color: #991b1b;
}

.badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.badge.low {
  background: #dbeafe;
  color: #1e40af;
}

.loading {
  text-align: center;
  padding: var(--sp-8);
  color: var(--text-muted);
  font-size: 0.938rem;
}

.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: var(--sp-4);
  border-radius: var(--radius-sm);
  margin: var(--sp-4) 0;
  font-size: 0.938rem;
}

/* ---------- Responsive ---------- */

/* 768px - 1280px: force the sidebar into its collapsed (icon-only) form,
   regardless of the user's persisted expand/collapse preference. */
@media (max-width: 1280px) {
  .app-shell {
    grid-template-columns: var(--sidebar-w-collapsed) 1fr !important;
  }

  .sidebar .nav-label,
  .sidebar .nav-section-label,
  .sidebar .brand-text {
    display: none !important;
  }

  .sidebar .sidebar-brand {
    justify-content: center !important;
    padding: var(--sp-5) var(--sp-2) !important;
  }

  .sidebar .sidebar-nav a,
  .sidebar .sidebar-toggle {
    justify-content: center !important;
  }
}

/* < 768px: sidebar becomes an off-canvas drawer, shown in full (uncollapsed)
   form when opened, regardless of the persisted desktop preference. */
@media (max-width: 768px) {
  .app-shell,
  .app-shell.collapsed {
    grid-template-columns: 1fr !important;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-w) !important;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    z-index: 200;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar .nav-label,
  .sidebar .nav-section-label,
  .sidebar .brand-text {
    display: block !important;
  }

  .sidebar .sidebar-brand {
    justify-content: flex-start !important;
    padding: var(--sp-5) var(--sp-4) !important;
  }

  .sidebar .sidebar-nav a,
  .sidebar .sidebar-toggle {
    justify-content: flex-start !important;
  }

  .sidebar-toggle {
    display: none !important;
  }

  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.45);
    z-index: 150;
  }

  .mobile-menu-btn {
    display: flex;
  }

  .topbar {
    padding: 0 var(--sp-4);
  }

  .main-content {
    padding: var(--sp-4);
  }
}
</style>
