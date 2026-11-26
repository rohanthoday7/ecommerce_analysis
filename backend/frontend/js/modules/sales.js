/**
 * Sales Analytics Module Renderer
 */

const SalesModule = {
  currentGrain: 'monthly',
  salesData: null,

  async render(container, filters) {
    container.innerHTML = `
      <div class="kpi-grid" id="sales-kpis">
        <div class="kpi-card"><div class="kpi-title">Loading Sales Analytics...</div></div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">Chronological Sales Evolution</div>
            <div class="card-desc">Interactive multi-grain revenue and order volume trends</div>
          </div>
          <div class="preset-pills">
            <button class="pill-btn ${this.currentGrain === 'daily' ? 'active' : ''}" onclick="SalesModule.switchGrain('daily')">Daily</button>
            <button class="pill-btn ${this.currentGrain === 'weekly' ? 'active' : ''}" onclick="SalesModule.switchGrain('weekly')">Weekly</button>
            <button class="pill-btn ${this.currentGrain === 'monthly' ? 'active' : ''}" onclick="SalesModule.switchGrain('monthly')">Monthly</button>
            <button class="pill-btn ${this.currentGrain === 'yearly' ? 'active' : ''}" onclick="SalesModule.switchGrain('yearly')">Yearly</button>
          </div>
        </div>
        <div class="chart-container" style="height: 340px;">
          <canvas id="sales-timeseries-chart"></canvas>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Month-over-Month (MoM) Growth Dynamics</div>
              <div class="card-desc">Sequential top-line percentage growth trajectory</div>
            </div>
          </div>
          <div class="chart-container" style="height: 280px;">
            <canvas id="sales-mom-chart"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Order Basket Size Distribution</div>
              <div class="card-desc">Transaction frequency grouped by check-out dollar tiers</div>
            </div>
          </div>
          <div class="chart-container" style="height: 280px;">
            <canvas id="sales-basket-chart"></canvas>
          </div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Annual Seasonality (Calendar Months)</div>
              <div class="card-desc">Aggregate historical demand curve from January through December</div>
            </div>
          </div>
          <div class="chart-container" style="height: 260px;">
            <canvas id="sales-monthly-seasonality-chart"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Day-of-Week Purchasing Cycle</div>
              <div class="card-desc">Conversion velocity by weekday (Monday through Sunday)</div>
            </div>
          </div>
          <div class="chart-container" style="height: 260px;">
            <canvas id="sales-dow-seasonality-chart"></canvas>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">Category Revenue Contribution & AOV</div>
            <div class="card-desc">Detailed departmental unit economics and sales share</div>
          </div>
        </div>
        <div class="table-wrapper">
          <table class="data-table" id="sales-category-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Revenue</th>
                <th>Share</th>
                <th>Orders</th>
                <th>Units Sold</th>
                <th>Average Order Value (AOV)</th>
              </tr>
            </thead>
            <tbody>
              <tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Loading table...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    try {
      this.salesData = await API.getSalesAnalytics(filters);
      this.populateKPIs(this.salesData.summary);
      this.renderTimeSeriesChart();
      this.renderMoMChart(this.salesData.mom_growth);
      this.renderSeasonalityCharts(this.salesData.seasonality);
      this.renderBasketChart(this.salesData.order_distribution);
      this.populateCategoryTable(this.salesData.category_performance);
    } catch (err) {
      container.innerHTML = `<div class="card" style="color: var(--accent-rose); padding: 2rem;">Error loading sales analytics: ${err.message}</div>`;
    }
  },

  switchGrain(grain) {
    this.currentGrain = grain;
    // Update pill buttons active state
    document.querySelectorAll('.preset-pills .pill-btn').forEach(btn => {
      btn.classList.toggle('active', btn.textContent.toLowerCase() === grain);
    });
    this.renderTimeSeriesChart();
  },

  populateKPIs(summary) {
    const kpiContainer = document.getElementById('sales-kpis');
    if (!kpiContainer || !summary) return;

    kpiContainer.innerHTML = `
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Total Recognized Revenue</span>
          <div class="kpi-icon-wrapper"><i data-lucide="trending-up"></i></div>
        </div>
        <div class="kpi-value">${Format.currency(summary.total_revenue)}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Delivered orders revenue</span></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Total Orders</span>
          <div class="kpi-icon-wrapper"><i data-lucide="shopping-cart"></i></div>
        </div>
        <div class="kpi-value">${Format.number(summary.total_orders)}</div>
        <div class="kpi-footer" style="flex-wrap: wrap; gap: 4px; font-size: 0.72rem;">
          <span style="color: var(--accent-emerald); font-weight: 600;">${Format.number(summary.delivered_orders || summary.total_orders)} Delivered</span>
          ${summary.cancelled_orders ? `<span style="color: var(--accent-rose); font-weight: 600;">&bull; ${Format.number(summary.cancelled_orders)} Cancelled</span>` : ''}
          ${summary.returned_orders ? `<span style="color: var(--accent-amber); font-weight: 600;">&bull; ${Format.number(summary.returned_orders)} Returned</span>` : ''}
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Average Order Value</span>
          <div class="kpi-icon-wrapper"><i data-lucide="credit-card"></i></div>
        </div>
        <div class="kpi-value">${Format.currency(summary.aov)}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Mean basket size</span></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Units Per Transaction</span>
          <div class="kpi-icon-wrapper"><i data-lucide="package"></i></div>
        </div>
        <div class="kpi-value">${summary.avg_units_per_order}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Basket item depth</span></div>
      </div>
    `;

    if (window.lucide) lucide.createIcons();
  },

  renderTimeSeriesChart() {
    if (!this.salesData || !this.salesData.time_series) return;
    const series = this.salesData.time_series[this.currentGrain] || {};

    ChartManager.createLineChart('sales-timeseries-chart', series.labels || [], [
      {
        label: 'Revenue (₹)',
        data: series.revenue || [],
        borderColor: ChartManager.colors.indigo,
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        fill: true,
        tension: 0.3,
        yAxisID: 'y'
      },
      {
        label: 'AOV (₹)',
        data: series.aov || [],
        borderColor: ChartManager.colors.cyan,
        borderDash: [3, 3],
        tension: 0.3,
        yAxisID: 'y'
      },
      {
        label: 'Orders',
        data: series.orders || [],
        borderColor: ChartManager.colors.emerald,
        borderDash: [5, 5],
        tension: 0.3,
        yAxisID: 'y1'
      }
    ], {
      scales: {
        y: {
          position: 'left',
          ticks: { callback: (v) => Format.compact(v) }
        },
        y1: {
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#10b981' }
        }
      }
    });
  },

  renderMoMChart(mom) {
    if (!mom || !mom.labels) return;

    const bgColors = (mom.growth_rates || []).map(val =>
      val >= 0 ? 'rgba(16, 185, 129, 0.8)' : 'rgba(244, 63, 94, 0.8)'
    );

    ChartManager.createBarChart('sales-mom-chart', mom.labels, [
      {
        label: 'MoM Growth (%)',
        data: mom.growth_rates,
        backgroundColor: bgColors,
        borderRadius: 4
      }
    ], {
      scales: {
        y: {
          ticks: { callback: (v) => `${v}%` }
        }
      }
    });
  },

  renderSeasonalityCharts(seasonality) {
    if (!seasonality) return;

    // Monthly
    const m = seasonality.monthly || {};
    ChartManager.createLineChart('sales-monthly-seasonality-chart', m.labels || [], [
      {
        label: 'Monthly Sales (₹)',
        data: m.revenue || [],
        borderColor: ChartManager.colors.amber,
        backgroundColor: 'rgba(245, 158, 11, 0.08)',
        fill: true,
        tension: 0.35
      }
    ], {
      scales: {
        y: { ticks: { callback: (v) => Format.compact(v) } }
      }
    });

    // Day of Week
    const d = seasonality.day_of_week || {};
    ChartManager.createBarChart('sales-dow-seasonality-chart', d.labels || [], [
      {
        label: 'Revenue by Day (₹)',
        data: d.revenue || [],
        backgroundColor: 'rgba(6, 182, 212, 0.8)',
        borderRadius: 6
      }
    ], {
      scales: {
        y: { ticks: { callback: (v) => Format.compact(v) } }
      }
    });
  },

  renderBasketChart(dist) {
    if (!dist || !dist.bins) return;

    ChartManager.createBarChart('sales-basket-chart', dist.bins, [
      {
        label: 'Order Count',
        data: dist.counts || [],
        backgroundColor: 'rgba(139, 92, 246, 0.8)',
        borderRadius: 6
      }
    ]);
  },

  populateCategoryTable(categories) {
    const tbody = document.querySelector('#sales-category-table tbody');
    if (!tbody || !categories) return;

    tbody.innerHTML = categories.map(c => `
      <tr>
        <td style="font-weight: 600; color: var(--text-primary);">${c.category}</td>
        <td style="font-weight: 700; color: var(--text-primary);">${Format.currency(c.revenue)}</td>
        <td>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>${c.share}%</span>
            <div style="flex: 1; max-width: 80px; height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden;">
              <div style="width: ${c.share}%; height: 100%; background: var(--accent-primary);"></div>
            </div>
          </div>
        </td>
        <td>${Format.number(c.orders)}</td>
        <td>${Format.number(c.quantity)}</td>
        <td style="color: var(--accent-emerald); font-weight: 600;">${Format.currency(c.aov)}</td>
      </tr>
    `).join('');
  }
};
