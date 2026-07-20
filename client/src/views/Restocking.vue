<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div class="card budget-card">
      <div class="budget-row">
        <label class="budget-label" for="budget-slider">{{ t('restocking.budget') }}</label>
        <span class="budget-value">{{ formatCurrency(budget, currentCurrency) }}</span>
      </div>
      <input
        id="budget-slider"
        v-model.number="budget"
        type="range"
        min="0"
        max="100000"
        step="1000"
        class="budget-slider"
      />
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div v-if="confirmation" class="confirmation">{{ confirmation }}</div>
      <div v-if="submitError" class="error">{{ submitError }}</div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.budget') }}</div>
          <div class="stat-value">{{ formatCurrency(budget, currentCurrency) }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.allocated') }}</div>
          <div class="stat-value">{{ formatCurrency(allocated, currentCurrency) }}</div>
        </div>
        <div class="stat-card" :class="{ danger: remaining < 0 }">
          <div class="stat-label">{{ t('restocking.remaining') }}</div>
          <div class="stat-value">{{ formatCurrency(remaining, currentCurrency) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.itemsSelected') }}</div>
          <div class="stat-value">{{ itemsSelected }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.title') }}</h3>
          <button
            class="place-order-btn"
            :disabled="!canPlaceOrder || placing"
            @click="placeOrder"
          >
            {{ t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="recommendations.length === 0" class="no-data">
          {{ t('restocking.noRecommendations') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.supplier') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th>{{ t('restocking.table.currentDemand') }}</th>
                <th>{{ t('restocking.table.forecastedDemand') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.quantity') }}</th>
                <th>{{ t('restocking.table.lineTotal') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in recommendations" :key="row.item_sku">
                <td><strong>{{ row.item_sku }}</strong></td>
                <td>{{ row.item_name }}</td>
                <td>{{ row.supplier }}</td>
                <td>
                  <span :class="['badge', row.trend]">
                    {{ t(`trends.${row.trend}`) }}
                  </span>
                </td>
                <td>{{ row.current_demand }}</td>
                <td>{{ row.forecasted_demand }}</td>
                <td>{{ formatCurrency(row.unit_cost, currentCurrency) }}</td>
                <td>
                  <input
                    type="number"
                    min="0"
                    class="quantity-input"
                    v-model.number="quantities[row.item_sku]"
                  />
                </td>
                <td><strong>{{ formatCurrency(lineTotal(row), currentCurrency) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency } from '../utils/currency'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency } = useI18n()

    const budget = ref(50000)
    const loading = ref(true)
    const error = ref(null)
    const recommendations = ref([])
    const quantities = reactive({})

    const placing = ref(false)
    const confirmation = ref(null)
    const submitError = ref(null)

    let debounceTimer = null

    const resetQuantities = () => {
      for (const key of Object.keys(quantities)) {
        delete quantities[key]
      }
      for (const row of recommendations.value) {
        quantities[row.item_sku] = row.recommended_quantity
      }
    }

    const loadRecommendations = async () => {
      try {
        loading.value = true
        error.value = null
        recommendations.value = await api.getRestockRecommendations(budget.value)
        resetQuantities()
      } catch (err) {
        error.value = 'Failed to load restock recommendations: ' + err.message
      } finally {
        loading.value = false
      }
    }

    watch(budget, () => {
      confirmation.value = null
      submitError.value = null
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        loadRecommendations()
      }, 300)
    })

    const lineTotal = (row) => {
      const qty = quantities[row.item_sku] || 0
      return qty * row.unit_cost
    }

    const allocated = computed(() => {
      return recommendations.value.reduce((sum, row) => sum + lineTotal(row), 0)
    })

    const remaining = computed(() => budget.value - allocated.value)

    const itemsSelected = computed(() => {
      return recommendations.value.filter(row => (quantities[row.item_sku] || 0) > 0).length
    })

    const canPlaceOrder = computed(() => {
      return itemsSelected.value > 0 && allocated.value <= budget.value
    })

    const placeOrder = async () => {
      confirmation.value = null
      submitError.value = null
      placing.value = true
      try {
        const items = recommendations.value
          .filter(row => (quantities[row.item_sku] || 0) > 0)
          .map(row => ({
            item_sku: row.item_sku,
            item_name: row.item_name,
            quantity: quantities[row.item_sku],
            unit_cost: row.unit_cost,
            supplier: row.supplier,
            lead_time_days: row.lead_time_days
          }))

        const result = await api.createRestockOrder({
          budget: budget.value,
          items
        })

        confirmation.value = t('restocking.orderPlaced', { orderNumber: result.order_number })
        resetQuantities()
      } catch (err) {
        submitError.value = err.response && err.response.status === 400
          ? t('restocking.overBudget')
          : ('Failed to place order: ' + err.message)
      } finally {
        placing.value = false
      }
    }

    onMounted(loadRecommendations)

    return {
      t,
      currentCurrency,
      formatCurrency,
      budget,
      loading,
      error,
      recommendations,
      quantities,
      lineTotal,
      allocated,
      remaining,
      itemsSelected,
      canPlaceOrder,
      placing,
      confirmation,
      submitError,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-card {
  margin-bottom: 1.5rem;
}

.budget-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.budget-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.budget-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
}

.budget-slider {
  width: 100%;
  accent-color: #3b82f6;
}

.confirmation {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.938rem;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-size: 0.938rem;
}

.quantity-input {
  width: 80px;
  padding: 0.375rem 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #0f172a;
}

.quantity-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.place-order-btn {
  background: #0f172a;
  color: white;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1e293b;
}

.place-order-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}
</style>
