<template>
  <div class="reports">
    <div class="page-header">
      <h2>{{ t("reports.title") }}</h2>
      <p>{{ t("reports.description") }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t("reports.loading") }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Quarterly Performance -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {{ t("reports.quarterlyPerformance.title") }}
          </h3>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t("reports.quarterlyPerformance.quarter") }}</th>
                <th>{{ t("reports.quarterlyPerformance.totalOrders") }}</th>
                <th>{{ t("reports.quarterlyPerformance.totalRevenue") }}</th>
                <th>{{ t("reports.quarterlyPerformance.avgOrderValue") }}</th>
                <th>{{ t("reports.quarterlyPerformance.fulfillmentRate") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(q, index) in quarterlyData" :key="index">
                <td>
                  <strong>{{ q.quarter }}</strong>
                </td>
                <td>{{ q.total_orders }}</td>
                <td>${{ formatNumber(q.total_revenue) }}</td>
                <td>${{ formatNumber(q.avg_order_value) }}</td>
                <td>
                  <span :class="getFulfillmentClass(q.fulfillment_rate)">
                    {{ q.fulfillment_rate }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Monthly Trends Chart -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t("reports.monthlyTrend.title") }}</h3>
        </div>
        <div class="chart-container">
          <div class="bar-chart">
            <div
              v-for="(month, index) in monthlyData"
              :key="index"
              class="bar-wrapper"
            >
              <div class="bar-container">
                <div
                  class="bar"
                  :style="{ height: getBarHeight(month.revenue) + 'px' }"
                  :title="'$' + formatNumber(month.revenue)"
                ></div>
              </div>
              <div class="bar-label">{{ formatMonth(month.month) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Month-over-Month Comparison -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t("reports.momAnalysis.title") }}</h3>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t("reports.momAnalysis.month") }}</th>
                <th>{{ t("reports.momAnalysis.orders") }}</th>
                <th>{{ t("reports.momAnalysis.revenue") }}</th>
                <th>{{ t("reports.momAnalysis.change") }}</th>
                <th>{{ t("reports.momAnalysis.growthRate") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(month, index) in monthlyData" :key="index">
                <td>
                  <strong>{{ formatMonth(month.month) }}</strong>
                </td>
                <td>{{ month.order_count }}</td>
                <td>${{ formatNumber(month.revenue) }}</td>
                <td>
                  <span
                    v-if="index > 0"
                    :class="
                      getChangeClass(
                        month.revenue,
                        monthlyData[index - 1].revenue,
                      )
                    "
                  >
                    {{
                      getChangeValue(
                        month.revenue,
                        monthlyData[index - 1].revenue,
                      )
                    }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td>
                  <span
                    v-if="index > 0"
                    :class="
                      getChangeClass(
                        month.revenue,
                        monthlyData[index - 1].revenue,
                      )
                    "
                  >
                    {{
                      getGrowthRate(
                        month.revenue,
                        monthlyData[index - 1].revenue,
                      )
                    }}
                  </span>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">
            {{ t("reports.summary.totalRevenueYtd") }}
          </div>
          <div class="stat-value">${{ formatNumber(totalRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">
            {{ t("reports.summary.avgMonthlyRevenue") }}
          </div>
          <div class="stat-value">${{ formatNumber(avgMonthlyRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">
            {{ t("reports.summary.totalOrdersYtd") }}
          </div>
          <div class="stat-value">{{ totalOrders }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t("reports.summary.bestQuarter") }}</div>
          <div class="stat-value">{{ bestQuarter }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { useI18n } from "../composables/useI18n";

export default {
  name: "Reports",
  setup() {
    const { t } = useI18n();
    return { t };
  },
  data() {
    return {
      loading: true,
      error: null,
      quarterlyData: [],
      monthlyData: [],
      totalRevenue: 0,
      avgMonthlyRevenue: 0,
      totalOrders: 0,
      bestQuarter: "",
    };
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      try {
        this.loading = true;

        // Fetch quarterly data
        const quarterlyResponse = await axios.get(
          "http://localhost:8001/api/reports/quarterly",
        );
        this.quarterlyData = quarterlyResponse.data;

        // Fetch monthly data
        const monthlyResponse = await axios.get(
          "http://localhost:8001/api/reports/monthly-trends",
        );
        this.monthlyData = monthlyResponse.data;

        // Calculate summary stats
        this.calculateSummaryStats();
      } catch (err) {
        this.error = "Failed to load reports: " + err.message;
      } finally {
        this.loading = false;
      }
    },

    calculateSummaryStats() {
      // Calculate total revenue
      let total = 0;
      for (let i = 0; i < this.monthlyData.length; i++) {
        total = total + this.monthlyData[i].revenue;
      }
      this.totalRevenue = total;

      // Calculate average monthly revenue
      if (this.monthlyData.length > 0) {
        this.avgMonthlyRevenue = total / this.monthlyData.length;
      } else {
        this.avgMonthlyRevenue = 0;
      }

      // Calculate total orders
      let orders = 0;
      for (let i = 0; i < this.monthlyData.length; i++) {
        orders = orders + this.monthlyData[i].order_count;
      }
      this.totalOrders = orders;

      // Find best quarter
      let bestQ = "";
      let bestRevenue = 0;
      for (let i = 0; i < this.quarterlyData.length; i++) {
        if (this.quarterlyData[i].total_revenue > bestRevenue) {
          bestRevenue = this.quarterlyData[i].total_revenue;
          bestQ = this.quarterlyData[i].quarter;
        }
      }
      this.bestQuarter = bestQ;
    },

    formatNumber(num) {
      // Format number with commas
      const str = num.toString();
      const parts = str.split(".");
      const intPart = parts[0];
      let decPart = parts.length > 1 ? parts[1] : "00";

      let formatted = "";
      let count = 0;
      for (let i = intPart.length - 1; i >= 0; i--) {
        if (count > 0 && count % 3 === 0) {
          formatted = "," + formatted;
        }
        formatted = intPart[i] + formatted;
        count++;
      }

      if (decPart.length === 1) {
        decPart = decPart + "0";
      }
      if (decPart.length > 2) {
        decPart = decPart.substring(0, 2);
      }

      return formatted + "." + decPart;
    },

    formatMonth(monthStr) {
      // Convert YYYY-MM to readable format
      const parts = monthStr.split("-");
      const year = parts[0];
      const month = parts[1];

      const monthNames = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ];
      const monthIndex = parseInt(month) - 1;

      return monthNames[monthIndex] + " " + year;
    },

    getBarHeight(revenue) {
      // Calculate bar height (max height 200px)
      let maxRevenue = 0;
      for (let i = 0; i < this.monthlyData.length; i++) {
        if (this.monthlyData[i].revenue > maxRevenue) {
          maxRevenue = this.monthlyData[i].revenue;
        }
      }

      if (maxRevenue === 0) {
        return 0;
      }

      const height = (revenue / maxRevenue) * 200;
      return height;
    },

    getFulfillmentClass(rate) {
      if (rate >= 90) {
        return "badge success";
      } else if (rate >= 75) {
        return "badge warning";
      } else {
        return "badge danger";
      }
    },

    getChangeValue(current, previous) {
      const change = current - previous;
      if (change > 0) {
        return "+$" + this.formatNumber(change);
      } else if (change < 0) {
        return "-$" + this.formatNumber(Math.abs(change));
      } else {
        return "$0.00";
      }
    },

    getChangeClass(current, previous) {
      const change = current - previous;
      if (change > 0) {
        return "positive-change";
      } else if (change < 0) {
        return "negative-change";
      } else {
        return "";
      }
    },

    getGrowthRate(current, previous) {
      if (previous === 0) {
        return "N/A";
      }

      const rate = ((current - previous) / previous) * 100;
      const sign = rate > 0 ? "+" : "";

      return sign + rate.toFixed(1) + "%";
    },
  },
};
</script>

<style scoped>
.reports {
  padding: 0;
}

.chart-container {
  padding: var(--sp-6) var(--sp-4);
  min-height: 300px;
  overflow-x: auto;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 250px;
  gap: var(--sp-2);
  min-width: 640px;
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 80px;
  min-width: 44px;
}

.bar-container {
  height: 200px;
  display: flex;
  align-items: flex-end;
  width: 100%;
}

.bar {
  width: 100%;
  background: var(--accent);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: all 0.3s;
  cursor: pointer;
}

.bar:hover {
  background: var(--accent-strong);
}

.bar-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
  transform: rotate(-45deg);
  white-space: nowrap;
  margin-top: var(--sp-5);
}

.stats-grid {
  margin-top: var(--sp-5);
}

.positive-change {
  color: var(--success);
  font-weight: 600;
}

.negative-change {
  color: var(--danger);
  font-weight: 600;
}
</style>
