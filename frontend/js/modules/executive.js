/**
 * Executive Dashboard Module Renderer
 */

const ExecutiveModule = {
  async render(container, filters) {
    container.innerHTML = `
      <div class="kpi-grid" id="exec-kpis">
        <div class="kpi-card"><div class="kpi-title">Loading KPIs...</div></div>
      </div>

      <div class="grid-2-1">
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Revenue & Order Velocity</div>
              <div class="card-desc">Chronological sales performance with average order value trajectory</div>
            </div>
          </div>
          <div class="chart-container" style="height: 320px;">
            <canvas id="exec-revenue-chart"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Revenue by Category</div>
              <div class="card-desc">Distribution of sales across product departments</div>
            </div>
          </div>
          <div class="chart-container" style="height: 320px;">
            <canvas id="exec-category-chart"></canvas>
          </div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Geographic Sales Volume</div>
              <div class="card-desc">Top regional territory revenue performance</div>
            </div>
          </div>
          <div class="chart-container" style="height: 280px;">
            <canvas id="exec-region-chart"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Customer Acquisition & Loyalty</div>
              <div class="card-desc">New customer intake vs repeat buyers</div>
            </div>
          </div>
          <div class="chart-container" style="height: 280px;">
            <canvas id="exec-customer-chart"></canvas>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">Top Performing Hero Products</div>
            <div class="card-desc">Highest revenue generating SKUs in the selected period</div>
          </div>
          <button class="btn btn-outline btn-sm" onclick="State.setModule('products')">View All Products →</button>
        </div>
        <div class="table-wrapper">
          <table class="data-table" id="exec-top-products-table">
            <thead>
              <tr>
                <th>Product SKU</th>
                <th>Product Name</th>
                <th>Category</th>
                <th>Orders</th>
                <th>Units Sold</th>
                <th>Total Revenue</th>
              </tr>
            </thead>
            <tbody>
              <tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Loading products...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    try {
      const data = await API.getExecutiveAnalytics(filters);
      this.populateKPIs(data.kpis);
      this.renderCharts(data);
      this.populateTable(data.top_products);
    } catch (err) {
      container.innerHTML = `<div class="card" style="color: var(--accent-rose); padding: 2rem;">Error loading executive analytics: ${err.message}</div>`;
    }
  },

  populateKPIs(kpis) {
    const kpiContainer = document.getElementById('exec-kpis');
    if (!kpiContainer || !kpis) return;

    const g = kpis.growth || {};

    const renderBadge = (growth) => {
      if (growth === undefined || growth === null || isNaN(growth)) return '';
      const isPos = growth >= 0;
      return `<span class="growth-badge ${isPos ? 'growth-positive' : 'growth-negative'}">${isPos ? '↑' : '↓'} ${Math.abs(growth)}%</span>`;
    };

    let profitKpi = '';
    if (kpis.has_profit_data && kpis.gross_profit !== null) {
      profitKpi = `
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Gross Profit</span>
            <div class="kpi-icon-wrapper"><i data-lucide="wallet"></i></div>
          </div>
          <div class="kpi-value">${Format.currency(kpis.gross_profit)}</div>
          <div class="kpi-footer">
            <span class="growth-badge growth-positive">${kpis.profit_margin}% Margin</span>
            <span class="kpi-subtext">Operating Profit</span>
          </div>
        </div>
      `;
    }

    kpiContainer.innerHTML = `
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Total Revenue</span>
          <div class="kpi-icon-wrapper"><i data-lucide="trending-up"></i></div>
        </div>
        <div class="kpi-value">${Format.currency(kpis.total_revenue)}</div>
        <div class="kpi-footer">
          ${renderBadge(g.revenue_growth)}
          <span class="kpi-subtext">vs previous period</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Total Orders</span>
          <div class="kpi-icon-wrapper"><i data-lucide="shopping-bag"></i></div>
        </div>
        <div class="kpi-value">${Format.number(kpis.total_orders)}</div>
        <div class="kpi-footer" style="flex-wrap: wrap; gap: 4px; font-size: 0.72rem;">
          <span style="color: var(--accent-emerald); font-weight: 600;">${Format.number(kpis.delivered_orders || kpis.total_orders)} Delivered</span>
          ${kpis.cancelled_orders ? `<span style="color: var(--accent-rose); font-weight: 600;">&bull; ${Format.number(kpis.cancelled_orders)} Cancelled</span>` : ''}
          ${kpis.returned_orders ? `<span style="color: var(--accent-amber); font-weight: 600;">&bull; ${Format.number(kpis.returned_orders)} Returned</span>` : ''}
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Avg Order Value (AOV)</span>
          <div class="kpi-icon-wrapper"><i data-lucide="credit-card"></i></div>
        </div>
        <div class="kpi-value">${Format.currency(kpis.average_order_value)}</div>
        <div class="kpi-footer">
          ${renderBadge(g.aov_growth)}
          <span class="kpi-subtext">Per checkout</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Active Customers</span>
          <div class="kpi-icon-wrapper"><i data-lucide="users"></i></div>
        </div>
        <div class="kpi-value">${Format.number(kpis.total_customers)}</div>
        <div class="kpi-footer">
          <span class="growth-badge growth-neutral">${kpis.repeat_purchase_rate}% Repeat</span>
          <span class="kpi-subtext">Customer Base</span>
        </div>
      </div>

      ${profitKpi}
    `;

    if (window.lucide) lucide.createIcons();
  },

  renderCharts(data) {
    // 1. Dual Axis Revenue & Orders Trend
    const rev = data.revenue_trend || {};
    ChartManager.createLineChart('exec-revenue-chart', rev.labels || [], [
      {
        label: 'Revenue (₹)',
        data: rev.revenue || [],
        borderColor: ChartManager.colors.indigo,
        backgroundColor: 'rgba(99, 102, 241, 0.08)',
        fill: true,
        tension: 0.35,
        yAxisID: 'y'
      },
      {
        label: 'Orders',
        data: rev.orders || [],
        borderColor: ChartManager.colors.emerald,
        borderDash: [4, 4],
        backgroundColor: 'transparent',
        tension: 0.35,
        yAxisID: 'y1'
      }
    ], {
      scales: {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            color: '#64748b',
            callback: (v) => Format.compact(v)
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#10b981' }
        }
      }
    });

    // 2. Category Doughnut Chart
    const cat = data.category_breakdown || {};
    ChartManager.createDoughnutChart('exec-category-chart', cat.labels || [], cat.values || []);

    // 3. Regional Revenue Bar Chart
    const reg = data.region_breakdown || {};
    ChartManager.createBarChart('exec-region-chart', reg.labels || [], [
      {
        label: 'Revenue (₹)',
        data: reg.values || [],
        backgroundColor: 'rgba(99, 102, 241, 0.8)',
        borderRadius: 6
      }
    ], {
      scales: {
        y: {
          ticks: { callback: (v) => Format.compact(v) }
        }
      }
    });

    // 4. Customer Breakdown
    const seg = data.segment_breakdown || {};
    ChartManager.createDoughnutChart('exec-customer-chart', seg.labels || [], seg.revenue || [], {
      plugins: {
        legend: { position: 'bottom' }
      }
    });
  },

  populateTable(products) {
    const tbody = document.querySelector('#exec-top-products-table tbody');
    if (!tbody) return;

    if (!products || products.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No products found.</td></tr>`;
      return;
    }

    tbody.innerHTML = products.map(p => `
      <tr>
        <td style="font-family: var(--font-mono); color: var(--accent-primary); font-size: 0.8rem;">${p.product_id}</td>
        <td style="font-weight: 600; color: var(--text-primary);">${p.product_name}</td>
        <td><span class="badge" style="background: rgba(255,255,255,0.06); color: var(--text-secondary);">${p.category}</span></td>
        <td>${Format.number(p.orders)}</td>
        <td>${Format.number(p.quantity)}</td>
        <td style="font-weight: 700; color: var(--text-primary);">${Format.currency(p.revenue)}</td>
      </tr>
    `).join('');
  }
};
