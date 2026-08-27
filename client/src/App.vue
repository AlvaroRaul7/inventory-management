<template>
  <div class="app-shell">
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-mark">{{ t("nav.companyName").charAt(0) }}</span>
          <div class="logo-text">
            <h1>{{ t("nav.companyName") }}</h1>
            <span class="subtitle">{{ t("nav.subtitle") }}</span>
          </div>
        </div>
        <button
          class="collapse-btn"
          @click="sidebarCollapsed = !sidebarCollapsed"
          title="Toggle sidebar"
        >
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fill-rule="evenodd"
              d="M4 5a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zm0 5a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zm0 5a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>

      <nav class="nav-links">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="{ active: $route.path === item.path }"
          :title="item.label"
          :aria-label="item.label"
        >
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path :d="item.icon" />
          </svg>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button
          class="theme-toggle-btn"
          @click="toggleTheme"
          :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
        >
          <svg
            v-if="isDark"
            class="theme-toggle-icon"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4.22 1.78a1 1 0 010 1.42l-.71.7a1 1 0 11-1.41-1.41l.7-.71a1 1 0 011.42 0zM17 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zm-1.78 4.22a1 1 0 01-1.42 0l-.7-.71a1 1 0 111.41-1.41l.71.7a1 1 0 010 1.42zM10 17a1 1 0 01-1-1v-1a1 1 0 112 0v1a1 1 0 01-1 1zm-4.22-1.78a1 1 0 010-1.42l.71-.7a1 1 0 111.41 1.41l-.7.71a1 1 0 01-1.42 0zM3 10a1 1 0 011-1h1a1 1 0 110 2H4a1 1 0 01-1-1zm1.78-4.22a1 1 0 011.42 0l.7.71A1 1 0 115.49 7.9l-.71-.7a1 1 0 010-1.42zM10 6a4 4 0 100 8 4 4 0 000-8z"
            />
          </svg>
          <svg
            v-else
            class="theme-toggle-icon"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"
            />
          </svg>
          <span class="theme-toggle-label">{{
            isDark ? "Light mode" : "Dark mode"
          }}</span>
        </button>
        <div class="sidebar-footer-row">
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="showProfileDetails = true"
            @show-tasks="showTasks = true"
          />
        </div>
      </div>
    </aside>

    <div class="main-column">
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
import { ref, onMounted, computed } from "vue";
import { api } from "./api";
import { useAuth } from "./composables/useAuth";
import { useI18n } from "./composables/useI18n";
import { useTheme } from "./composables/useTheme";
import FilterBar from "./components/FilterBar.vue";
import ProfileMenu from "./components/ProfileMenu.vue";
import ProfileDetailsModal from "./components/ProfileDetailsModal.vue";
import TasksModal from "./components/TasksModal.vue";
import LanguageSwitcher from "./components/LanguageSwitcher.vue";

export default {
  name: "App",
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher,
  },
  setup() {
    const { currentUser } = useAuth();
    const { t } = useI18n();
    const { isDark, toggleTheme } = useTheme();
    const showProfileDetails = ref(false);
    const showTasks = ref(false);
    const apiTasks = ref([]);
    const sidebarCollapsed = ref(false);

    // Icon paths (24x24 stroke grid) keyed by route so nav stays in sync with the router
    const navItems = computed(() => [
      {
        path: "/",
        label: t("nav.overview"),
        icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
      },
      {
        path: "/inventory",
        label: t("nav.inventory"),
        icon: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
      },
      {
        path: "/orders",
        label: t("nav.orders"),
        icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
      },
      {
        path: "/spending",
        label: t("nav.finance"),
        icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V6m0 2v8m0 0v2m0-2c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
      },
      {
        path: "/demand",
        label: t("nav.demandForecast"),
        icon: "M3 17l6-6 4 4 8-8M21 7v6h-6",
      },
      {
        path: "/restocking",
        label: t("nav.restocking"),
        icon: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4M12 11v6",
      },
      {
        path: "/reports",
        label: "Reports",
        icon: "M9 19V6l7-3v13M9 19l-6-2V8l6-2m0 13l7-3M4 6l6 2m7 8v-6h4v6h-4z",
      },
    ]);

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

    return {
      t,
      isDark,
      toggleTheme,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask,
      sidebarCollapsed,
      navItems,
    };
  },
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --sidebar-w: 260px;
  --sidebar-w-collapsed: 76px;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 40px;
  --space-8: 48px;

  --radius-sm: 6px;
  --radius: 10px;
  --radius-lg: 14px;

  --bg: #f8fafc;
  --panel: #ffffff;
  --border: #e2e8f0;
  --border-soft: #f1f5f9;

  --text: #0f172a;
  --text-secondary: #334155;
  --muted: #64748b;

  --accent: #2563eb;
  --accent-hover: #1d4ed8;
  --accent-soft: #eff6ff;

  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 4px 16px rgba(15, 23, 42, 0.06);
  --shadow-lg: 0 12px 32px rgba(15, 23, 42, 0.1);
}

:root[data-theme="dark"] {
  --bg: #0f172a;
  --panel: #1e293b;
  --border: #334155;
  --border-soft: #293548;

  --text: #f1f5f9;
  --text-secondary: #cbd5e1;
  --muted: #94a3b8;

  --accent: #3b82f6;
  --accent-hover: #60a5fa;
  --accent-soft: rgba(59, 130, 246, 0.15);

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.35);
  --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.45);
}

:root[data-theme="dark"] th {
  color: var(--muted);
}

:root[data-theme="dark"] .badge.success {
  background: rgba(16, 185, 129, 0.18);
  color: #6ee7b7;
}

:root[data-theme="dark"] .badge.warning {
  background: rgba(249, 115, 22, 0.18);
  color: #fdba74;
}

:root[data-theme="dark"] .badge.danger {
  background: rgba(239, 68, 68, 0.18);
  color: #fca5a5;
}

:root[data-theme="dark"] .badge.info {
  background: rgba(59, 130, 246, 0.18);
  color: #93c5fd;
}

:root[data-theme="dark"] .badge.increasing {
  background: rgba(16, 185, 129, 0.18);
  color: #6ee7b7;
}

:root[data-theme="dark"] .badge.decreasing {
  background: rgba(239, 68, 68, 0.18);
  color: #fca5a5;
}

:root[data-theme="dark"] .badge.stable {
  background: rgba(99, 102, 241, 0.18);
  color: #c7d2fe;
}

:root[data-theme="dark"] .badge.high {
  background: rgba(239, 68, 68, 0.18);
  color: #fca5a5;
}

:root[data-theme="dark"] .badge.medium {
  background: rgba(249, 115, 22, 0.18);
  color: #fdba74;
}

:root[data-theme="dark"] .badge.low {
  background: rgba(59, 130, 246, 0.18);
  color: #93c5fd;
}

:root[data-theme="dark"] .error {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #fca5a5;
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
  background: var(--bg);
  color: var(--text-secondary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr;
  min-height: 100vh;
  transition: grid-template-columns 0.2s ease;
}

/* ---------- Sidebar ---------- */

.sidebar {
  background: var(--panel);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
  transition: width 0.2s ease;
  z-index: 100;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  padding: var(--space-5) var(--space-4) var(--space-6);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.logo-mark {
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
}

.logo-text {
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
}

.logo h1 {
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.subtitle {
  display: block;
  font-size: 0.75rem;
  color: var(--muted);
  font-weight: 400;
}

.collapse-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--muted);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.collapse-btn:hover {
  background: var(--border-soft);
  color: var(--text);
}
.collapse-btn svg {
  width: 16px;
  height: 16px;
}

.nav-links {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: 0 var(--space-3);
  overflow-y: auto;
}

.nav-links a {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-3);
  color: var(--muted);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  border-radius: var(--radius-sm);
  transition:
    background 0.15s ease,
    color 0.15s ease;
  white-space: nowrap;
}

.nav-links a:hover {
  color: var(--text);
  background: var(--border-soft);
}

.nav-links a.active {
  color: var(--accent);
  background: var(--accent-soft);
  font-weight: 600;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}
.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-3);
  border-top: 1px solid var(--border-soft);
}

.sidebar-footer-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: none;
  background: transparent;
  color: var(--muted);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
}

.theme-toggle-btn:hover {
  background: var(--border-soft);
  color: var(--text);
}

.theme-toggle-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.theme-toggle-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Collapsed / icon-rail state */
.app-shell:has(.sidebar.collapsed) {
  grid-template-columns: var(--sidebar-w-collapsed) 1fr;
}
.sidebar.collapsed {
  width: var(--sidebar-w-collapsed);
}
.sidebar.collapsed .logo-text,
.sidebar.collapsed .nav-label,
.sidebar.collapsed .theme-toggle-label {
  display: none;
}
.sidebar.collapsed .sidebar-header {
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
}
.sidebar.collapsed .collapse-btn {
  display: none;
}
.sidebar.collapsed .nav-links a {
  justify-content: center;
}
.sidebar.collapsed .theme-toggle-btn {
  justify-content: center;
}
.sidebar.collapsed:hover,
.sidebar.collapsed:focus-within {
  width: var(--sidebar-w);
  position: fixed;
  box-shadow: var(--shadow-lg);
}
.sidebar.collapsed:hover .logo-text,
.sidebar.collapsed:hover .nav-label,
.sidebar.collapsed:hover .theme-toggle-label,
.sidebar.collapsed:focus-within .logo-text,
.sidebar.collapsed:focus-within .nav-label,
.sidebar.collapsed:focus-within .theme-toggle-label {
  display: block;
}
.sidebar.collapsed:hover .sidebar-header,
.sidebar.collapsed:focus-within .sidebar-header {
  justify-content: space-between;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}
.sidebar.collapsed:hover .collapse-btn,
.sidebar.collapsed:focus-within .collapse-btn {
  display: flex;
}
.sidebar.collapsed:hover .nav-links a,
.sidebar.collapsed:focus-within .nav-links a {
  justify-content: flex-start;
}
.sidebar.collapsed:hover .theme-toggle-btn,
.sidebar.collapsed:focus-within .theme-toggle-btn {
  justify-content: flex-start;
}

@media (max-width: 900px) {
  .app-shell {
    grid-template-columns: var(--sidebar-w-collapsed) 1fr;
  }
  .sidebar {
    width: var(--sidebar-w-collapsed);
  }
  .sidebar .logo-text,
  .sidebar .nav-label {
    display: none;
  }
  .sidebar .sidebar-header {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }
  .sidebar .collapse-btn {
    display: none;
  }
  .sidebar .nav-links a {
    justify-content: center;
  }
}

/* ---------- Main column ---------- */

.main-column {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.main-content {
  flex: 1;
  width: 100%;
  padding: var(--space-6) var(--space-7);
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: var(--space-2);
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--muted);
  font-size: 0.938rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--panel);
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: #cbd5e1;
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.stat-label {
  color: var(--muted);
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-3);
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: #ea580c;
}

.stat-card.success .stat-value {
  color: #059669;
}

.stat-card.danger .stat-value {
  color: #dc2626;
}

.stat-card.info .stat-value {
  color: #2563eb;
}

.card {
  background: var(--panel);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--text);
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
  background: var(--bg);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

th {
  text-align: left;
  padding: var(--space-3) var(--space-4);
  font-weight: 600;
  color: #475569;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--border-soft);
  color: var(--text-secondary);
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--bg);
}

.badge {
  display: inline-block;
  padding: 0.313rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
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
  padding: var(--space-8);
  color: var(--muted);
  font-size: 0.938rem;
}

.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: var(--space-4);
  border-radius: var(--radius);
  margin: var(--space-4) 0;
  font-size: 0.938rem;
}
</style>
