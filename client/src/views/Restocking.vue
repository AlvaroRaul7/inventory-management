<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t("restocking.title") }}</h2>
      <p>{{ t("restocking.description") }}</p>
    </div>

    <div class="card">
      <div class="budget-slider-row">
        <label class="budget-label" for="budget-slider">{{
          t("restocking.budgetLabel")
        }}</label>
        <input
          id="budget-slider"
          v-model.number="budget"
          type="range"
          min="0"
          max="50000"
          step="500"
          class="budget-range"
        />
        <span class="budget-value">{{
          formatCurrency(budget, currentCurrency)
        }}</span>
      </div>
    </div>

    <div v-if="successMessage" class="success-banner">{{ successMessage }}</div>
    <div v-if="orderError" class="error">{{ orderError }}</div>

    <div v-if="loading" class="loading">{{ t("common.loading") }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t("restocking.totalCost") }}</div>
          <div class="stat-value">
            {{ formatCurrencyWithDecimals(totalCost, currentCurrency, 2) }}
          </div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t("restocking.remainingBudget") }}</div>
          <div class="stat-value">
            {{
              formatCurrencyWithDecimals(remainingBudget, currentCurrency, 2)
            }}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {{ t("restocking.recommendations") }} ({{ recommendations.length }})
          </h3>
          <button
            class="place-order-btn"
            :disabled="recommendations.length === 0 || placingOrder"
            @click="placeOrder"
          >
            {{
              placingOrder
                ? t("restocking.placingOrder")
                : t("restocking.placeOrder")
            }}
          </button>
        </div>
        <div v-if="recommendations.length === 0" class="no-data">
          {{ t("restocking.noRecommendations") }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t("restocking.table.sku") }}</th>
                <th>{{ t("restocking.table.itemName") }}</th>
                <th>{{ t("restocking.table.currentDemand") }}</th>
                <th>{{ t("restocking.table.forecastedDemand") }}</th>
                <th>{{ t("restocking.table.shortfall") }}</th>
                <th>{{ t("restocking.table.trend") }}</th>
                <th>{{ t("restocking.table.recommendedQuantity") }}</th>
                <th>{{ t("restocking.table.unitCost") }}</th>
                <th>{{ t("restocking.table.subtotal") }}</th>
                <th>{{ t("restocking.table.leadTime") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rec in recommendations" :key="rec.item_sku">
                <td>
                  <strong>{{ rec.item_sku }}</strong>
                </td>
                <td>{{ translateProductName(rec.item_name) }}</td>
                <td>{{ rec.current_demand }}</td>
                <td>{{ rec.forecasted_demand }}</td>
                <td>{{ rec.shortfall }}</td>
                <td>
                  <span :class="['badge', rec.trend]">
                    {{ t(`trends.${rec.trend}`) }}
                  </span>
                </td>
                <td>
                  <strong>{{ rec.recommended_quantity }}</strong>
                </td>
                <td>
                  {{
                    formatCurrencyWithDecimals(
                      rec.unit_cost,
                      currentCurrency,
                      2,
                    )
                  }}
                </td>
                <td>
                  {{
                    formatCurrencyWithDecimals(rec.subtotal, currentCurrency, 2)
                  }}
                </td>
                <td>{{ rec.lead_time_days }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { api } from "../api";
import { useI18n } from "../composables/useI18n";
import { formatCurrency, formatCurrencyWithDecimals } from "../utils/currency";

export default {
  name: "Restocking",
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n();

    const budget = ref(10000);
    const loading = ref(true);
    const error = ref(null);
    const recommendations = ref([]);
    const totalCost = ref(0);
    const remainingBudget = ref(0);
    const placingOrder = ref(false);
    const successMessage = ref(null);
    const orderError = ref(null);

    let debounceTimer = null;

    const loadRecommendations = async () => {
      try {
        loading.value = true;
        error.value = null;
        const data = await api.getDemandRecommendations(budget.value);
        recommendations.value = data.recommendations;
        totalCost.value = data.total_cost;
        remainingBudget.value = data.remaining_budget;
      } catch (err) {
        error.value = "Failed to load recommendations: " + err.message;
      } finally {
        loading.value = false;
      }
    };

    watch(budget, () => {
      successMessage.value = null;
      orderError.value = null;
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        loadRecommendations();
      }, 300);
    });

    const placeOrder = async () => {
      if (recommendations.value.length === 0) return;
      placingOrder.value = true;
      orderError.value = null;
      successMessage.value = null;
      try {
        await api.createRestockOrder({
          items: recommendations.value.map((rec) => ({
            item_sku: rec.item_sku,
            item_name: rec.item_name,
            quantity: rec.recommended_quantity,
            unit_cost: rec.unit_cost,
            lead_time_days: rec.lead_time_days,
            supplier_name: "Default Supplier",
          })),
          notes: "",
        });
        successMessage.value = t("restocking.orderSuccess");
        await loadRecommendations();
      } catch (err) {
        orderError.value = t("restocking.orderError") + ": " + err.message;
      } finally {
        placingOrder.value = false;
      }
    };

    onMounted(loadRecommendations);
    onUnmounted(() => {
      if (debounceTimer) clearTimeout(debounceTimer);
    });

    return {
      t,
      currentCurrency,
      translateProductName,
      budget,
      loading,
      error,
      recommendations,
      totalCost,
      remainingBudget,
      placingOrder,
      successMessage,
      orderError,
      placeOrder,
      formatCurrency,
      formatCurrencyWithDecimals,
    };
  },
};
</script>

<style scoped>
.budget-slider-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.budget-label {
  font-weight: 600;
  color: #475569;
  font-size: 0.938rem;
  white-space: nowrap;
}

.budget-range {
  flex: 1;
  height: 6px;
  border-radius: 8px;
  background: #e2e8f0;
  outline: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.budget-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  transition: background 0.2s ease;
}

.budget-range::-webkit-slider-thumb:hover {
  background: #2563eb;
}

.budget-range::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #3b82f6;
  border: none;
  cursor: pointer;
}

.budget-range:focus::-webkit-slider-thumb {
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}

.budget-value {
  font-weight: 700;
  color: #0f172a;
  font-size: 1.125rem;
  min-width: 100px;
  text-align: right;
}

.place-order-btn {
  padding: 0.625rem 1.25rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    opacity 0.2s ease,
    box-shadow 0.2s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.place-order-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.success-banner {
  background: #d1fae5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.938rem;
  font-weight: 500;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-size: 0.938rem;
}
</style>
