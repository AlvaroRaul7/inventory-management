<template>
  <div class="backlog">
    <div class="page-header">
      <h2>{{ t("backlog.title") }}</h2>
      <p>{{ t("backlog.description") }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t("common.loading") }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card danger">
          <div class="stat-label">{{ t("backlog.stats.highPriority") }}</div>
          <div class="stat-value">
            {{ getBacklogByPriority("high").length }}
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t("backlog.stats.mediumPriority") }}</div>
          <div class="stat-value">
            {{ getBacklogByPriority("medium").length }}
          </div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t("backlog.stats.lowPriority") }}</div>
          <div class="stat-value">{{ getBacklogByPriority("low").length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t("backlog.stats.totalItems") }}</div>
          <div class="stat-value">{{ backlogItems.length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {{ t("backlog.itemsTitle") }} ({{ backlogItems.length }})
          </h3>
        </div>
        <div v-if="backlogItems.length === 0" class="no-backlog">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            class="success-icon"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clip-rule="evenodd"
            />
          </svg>
          <p class="no-backlog-text">
            {{ t("dashboard.inventoryShortages.noShortages") }}
          </p>
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t("dashboard.inventoryShortages.orderId") }}</th>
                <th>{{ t("dashboard.inventoryShortages.sku") }}</th>
                <th>{{ t("dashboard.inventoryShortages.itemName") }}</th>
                <th>{{ t("dashboard.inventoryShortages.quantityNeeded") }}</th>
                <th>
                  {{ t("dashboard.inventoryShortages.quantityAvailable") }}
                </th>
                <th>{{ t("dashboard.inventoryShortages.shortage") }}</th>
                <th>{{ t("dashboard.inventoryShortages.daysDelayed") }}</th>
                <th>{{ t("dashboard.inventoryShortages.priority") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in backlogItems" :key="item.id">
                <td>
                  <strong>{{ item.order_id }}</strong>
                </td>
                <td>
                  <strong>{{ item.item_sku }}</strong>
                </td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.quantity_needed }}</td>
                <td>{{ item.quantity_available }}</td>
                <td>
                  <span class="badge danger">
                    {{ item.quantity_needed - item.quantity_available }}
                    {{ t("dashboard.inventoryShortages.unitsShort") }}
                  </span>
                </td>
                <td>
                  <span
                    :class="
                      item.days_delayed > 7
                        ? 'days-delayed-critical'
                        : 'days-delayed-warning'
                    "
                  >
                    {{ item.days_delayed }}
                    {{ t("dashboard.inventoryShortages.days") }}
                  </span>
                </td>
                <td>
                  <span :class="['badge', item.priority]">
                    {{ translatePriority(item.priority) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from "vue";
import { api } from "../api";
import { useFilters } from "../composables/useFilters";
import { useI18n } from "../composables/useI18n";

export default {
  name: "Backlog",
  setup() {
    const { t } = useI18n();

    const loading = ref(true);
    const error = ref(null);
    const allBacklogItems = ref([]);
    const inventoryItems = ref([]);

    // Use shared filters
    const { selectedLocation, selectedCategory, getCurrentFilters } =
      useFilters();

    // Filter backlog based on inventory filters
    const backlogItems = computed(() => {
      if (
        selectedLocation.value === "all" &&
        selectedCategory.value === "all"
      ) {
        return allBacklogItems.value;
      }

      // Get SKUs of items that match the filters
      const validSkus = new Set(inventoryItems.value.map((item) => item.sku));
      return allBacklogItems.value.filter((b) => validSkus.has(b.item_sku));
    });

    const loadBacklog = async () => {
      try {
        loading.value = true;
        const filters = getCurrentFilters();

        const [backlogData, inventoryData] = await Promise.all([
          api.getBacklog(),
          api.getInventory({
            warehouse: filters.warehouse,
            category: filters.category,
          }),
        ]);

        allBacklogItems.value = backlogData;
        inventoryItems.value = inventoryData;
      } catch (err) {
        error.value = "Failed to load backlog: " + err.message;
      } finally {
        loading.value = false;
      }
    };

    const getBacklogByPriority = (priority) => {
      return backlogItems.value.filter((item) => item.priority === priority);
    };

    const translatePriority = (priority) => {
      const map = {
        high: t("priority.high"),
        medium: t("priority.medium"),
        low: t("priority.low"),
        High: t("priority.high"),
        Medium: t("priority.medium"),
        Low: t("priority.low"),
      };
      return map[priority] || priority;
    };

    // Watch for filter changes and reload data
    watch([selectedLocation, selectedCategory], () => {
      loadBacklog();
    });

    onMounted(loadBacklog);

    return {
      t,
      loading,
      error,
      backlogItems,
      getBacklogByPriority,
      translatePriority,
    };
  },
};
</script>

<style scoped>
.no-backlog {
  padding: 3rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.success-icon {
  width: 48px;
  height: 48px;
  color: #10b981;
}

.no-backlog-text {
  font-size: 1.125rem;
  color: #10b981;
  font-weight: 600;
  margin: 0;
}

.days-delayed-critical {
  color: #ef4444;
}

.days-delayed-warning {
  color: #f59e0b;
}
</style>
