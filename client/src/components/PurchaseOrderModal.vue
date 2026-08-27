<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{
                mode === "create"
                  ? "Create Purchase Order"
                  : "Purchase Order Details"
              }}
            </h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path
                  d="M15 5L5 15M5 5L15 15"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="shortage-header">
              <div class="shortage-title-section">
                <h4 class="item-name">{{ backlogItem.item_name }}</h4>
                <div class="item-sku">SKU: {{ backlogItem.item_sku }}</div>
              </div>
            </div>

            <!-- CREATE MODE -->
            <form
              v-if="mode === 'create'"
              class="po-form"
              @submit.prevent="submitOrder"
            >
              <div class="form-grid">
                <div class="form-field">
                  <label class="form-label" for="supplier">Supplier Name</label>
                  <input
                    id="supplier"
                    v-model="form.supplier_name"
                    type="text"
                    class="form-input"
                    required
                  />
                </div>

                <div class="form-field">
                  <label class="form-label" for="quantity">Quantity</label>
                  <input
                    id="quantity"
                    v-model.number="form.quantity"
                    type="number"
                    min="1"
                    step="1"
                    class="form-input"
                    required
                  />
                </div>

                <div class="form-field">
                  <label class="form-label" for="unit-cost">Unit Cost</label>
                  <input
                    id="unit-cost"
                    v-model.number="form.unit_cost"
                    type="number"
                    min="0.01"
                    step="0.01"
                    class="form-input"
                    required
                  />
                </div>

                <div class="form-field">
                  <label class="form-label" for="lead-time"
                    >Lead Time (days)</label
                  >
                  <input
                    id="lead-time"
                    v-model.number="form.lead_time_days"
                    type="number"
                    min="0"
                    max="365"
                    step="1"
                    class="form-input"
                    required
                  />
                </div>
              </div>

              <div class="form-field full">
                <label class="form-label" for="notes">Notes (optional)</label>
                <textarea
                  id="notes"
                  v-model="form.notes"
                  class="form-textarea"
                  rows="3"
                ></textarea>
              </div>

              <div v-if="submitError" class="form-error">{{ submitError }}</div>
            </form>

            <!-- VIEW MODE -->
            <div v-else>
              <div v-if="viewLoading" class="loading-state">
                Loading purchase order...
              </div>
              <div v-else-if="!purchaseOrder" class="loading-state">
                Purchase order not found.
              </div>
              <div v-else class="info-grid">
                <div class="info-item">
                  <div class="info-label">Order Number</div>
                  <div class="info-value order-id">
                    {{ purchaseOrder.order_number }}
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-label">Supplier</div>
                  <div class="info-value">
                    {{ purchaseOrder.supplier_name }}
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-label">Quantity</div>
                  <div class="info-value">
                    {{ purchaseOrder.quantity }} units
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-label">Unit Cost</div>
                  <div class="info-value">${{ purchaseOrder.unit_cost }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Lead Time</div>
                  <div class="info-value">
                    {{ purchaseOrder.lead_time_days }} days
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-label">Expected Delivery</div>
                  <div class="info-value">
                    {{ formatDate(purchaseOrder.expected_delivery_date) }}
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-label">Status</div>
                  <div class="info-value">
                    <span class="badge">{{ purchaseOrder.status }}</span>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-label">Created Date</div>
                  <div class="info-value">
                    {{ formatDate(purchaseOrder.created_date) }}
                  </div>
                </div>
                <div class="info-item full" v-if="purchaseOrder.notes">
                  <div class="info-label">Notes</div>
                  <div class="info-value">{{ purchaseOrder.notes }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <template v-if="mode === 'create'">
              <button
                class="btn-secondary"
                type="button"
                @click="close"
                :disabled="submitting"
              >
                Cancel
              </button>
              <button
                class="btn-primary"
                type="button"
                @click="submitOrder"
                :disabled="submitting"
              >
                {{ submitting ? "Creating..." : "Create Purchase Order" }}
              </button>
            </template>
            <template v-else>
              <button class="btn-secondary" @click="close">Close</button>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch } from "vue";
import { api } from "../api";

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  backlogItem: {
    type: Object,
    default: null,
  },
  mode: {
    type: String,
    default: "create",
  },
});

const emit = defineEmits(["close", "po-created"]);

const form = reactive({
  supplier_name: "",
  quantity: 0,
  unit_cost: 0,
  lead_time_days: 7,
  notes: "",
});

const submitting = ref(false);
const submitError = ref(null);

const viewLoading = ref(false);
const purchaseOrder = ref(null);

const resetForm = () => {
  form.supplier_name = "";
  form.quantity = props.backlogItem ? props.backlogItem.quantity_needed : 0;
  form.unit_cost = 0;
  form.lead_time_days = 7;
  form.notes = "";
  submitError.value = null;
};

const loadPurchaseOrder = async () => {
  purchaseOrder.value = null;
  if (!props.backlogItem) return;

  if (props.backlogItem.purchase_order) {
    purchaseOrder.value = props.backlogItem.purchase_order;
    return;
  }

  viewLoading.value = true;
  try {
    const orders = await api.getPurchaseOrders();
    let match = orders.find((o) => o.backlog_item_id === props.backlogItem.id);
    if (!match) {
      match = orders.find((o) => o.item_sku === props.backlogItem.item_sku);
    }
    purchaseOrder.value = match || null;
  } catch (err) {
    console.error(err);
    purchaseOrder.value = null;
  } finally {
    viewLoading.value = false;
  }
};

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      if (props.mode === "create") {
        resetForm();
      } else {
        loadPurchaseOrder();
      }
    }
  },
);

const close = () => {
  emit("close");
};

const submitOrder = async () => {
  submitError.value = null;

  if (!form.supplier_name || form.quantity <= 0 || form.unit_cost <= 0) {
    submitError.value = "Please fill in all required fields with valid values.";
    return;
  }

  submitting.value = true;
  try {
    const orders = await api.createRestockOrder({
      items: [
        {
          item_sku: props.backlogItem.item_sku,
          item_name: props.backlogItem.item_name,
          quantity: form.quantity,
          unit_cost: form.unit_cost,
          lead_time_days: form.lead_time_days,
          supplier_name: form.supplier_name,
        },
      ],
      notes: form.notes,
    });

    const createdOrder = orders[0];
    const orderWithBacklogLink = {
      ...createdOrder,
      backlog_item_id: props.backlogItem.id,
    };

    emit("po-created", orderWithBacklogLink);
  } catch (err) {
    console.error(err);
    submitError.value = err.response?.data?.detail
      ? Array.isArray(err.response.data.detail)
        ? err.response.data.detail.map((d) => d.msg).join(", ")
        : err.response.data.detail
      : "Failed to create purchase order. Please check your inputs.";
  } finally {
    submitting.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return "N/A";
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.close-button {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.shortage-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.shortage-title-section {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
}

.item-sku {
  font-size: 0.875rem;
  color: #64748b;
  font-family: "Monaco", "Courier New", monospace;
}

.po-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field.full {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.form-input,
.form-textarea {
  padding: 0.625rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.938rem;
  font-family: inherit;
  color: #0f172a;
  transition: border-color 0.15s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

.form-textarea {
  resize: vertical;
}

.form-error {
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.875rem;
}

.loading-state {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item.full {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.info-value {
  font-size: 0.938rem;
  color: #0f172a;
  font-weight: 500;
}

.info-value.order-id {
  font-family: "Monaco", "Courier New", monospace;
  color: #2563eb;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 6px;
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: capitalize;
  background: #dbeafe;
  color: #1e40af;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: #3b82f6;
  border: 1px solid #3b82f6;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  border-color: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
