/**
 * Customer Intelligence & RFM Segmentation Module Renderer
 */

const CustomerModule = {
  highValueCustomers: [],

  async render(container, filters) {
    container.innerHTML = `
      <div class="kpi-grid" id="customer-kpis">
        <div class="kpi-card"><div class="kpi-title">Loading Customer Intelligence...</div></div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">New vs. Returning Customer Revenue</div>
              <div class="card-desc">Monthly cohort contribution to total sales volume</div>
            </div>
          </div>
          <div class="chart-container" style="height: 300px;">
            <canvas id="customer-cohort-chart"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Purchase Frequency Distribution</div>
              <div class="card-desc">Customer count bucketed by total lifetime orders placed</div>
            </div>
          </div>
          <div class="chart-container" style="height: 300px;">
            <canvas id="customer-frequency-chart"></canvas>
          </div>
        </div>
      </div>

      <!-- RFM Segmentation Grid -->
      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">RFM Strategic Behavioral Segmentation</div>
            <div class="card-desc">Empirical Recency (R), Frequency (F), Monetary (M) clustering</div>
          </div>
        </div>
        <div class="grid-3" id="rfm-segment-cards" style="margin-bottom: 1.5rem;"></div>
      </div>

      <!-- High-Value Customers Table -->
      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">High-Value Customer Profiles (Top Spenders)</div>
            <div class="card-desc">Individual VIP accounts driving significant enterprise top-line</div>
          </div>
          <div style="display: flex; gap: 0.5rem;">
            <input type="text" id="cust-search" class="filter-group" placeholder="Search customer or ID..." style="background: var(--bg-tertiary); color: #fff; width: 220px;" oninput="CustomerModule.filterTable(this.value)">
          </div>
        </div>
        <div class="table-wrapper">
          <table class="data-table" id="high-value-customers-table">
            <thead>
              <tr>
                <th>Customer Name & ID</th>
                <th>Segment</th>
                <th>RFM Status</th>
                <th>Total Spend</th>
                <th>Orders</th>
                <th>AOV</th>
                <th>Last Active</th>
                <th>Top Category</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    `;

    try {
      const data = await API.getCustomerAnalytics(filters);
      this.highValueCustomers = data.high_value_customers || [];
      this.populateKPIs(data.summary);
      this.renderCohortChart(data.new_vs_returning_trends);
      this.renderFrequencyChart(data.repeat_distribution);
      this.renderRfmSegments(data.rfm_segments);
      this.populateTable(this.highValueCustomers);
    } catch (err) {
      container.innerHTML = `<div class="card" style="color: var(--accent-rose); padding: 2rem;">Error loading customer analytics: ${err.message}</div>`;
    }
  },

  populateKPIs(summary) {
    const kpiContainer = document.getElementById('customer-kpis');
    if (!kpiContainer || !summary) return;

    kpiContainer.innerHTML = `
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Total Customer Base</span>
          <div class="kpi-icon-wrapper"><i data-lucide="users"></i></div>
        </div>
        <div class="kpi-value">${Format.number(summary.total_customers)}</div>
        <div class="kpi-footer">
          <span class="growth-badge growth-positive">${summary.repeat_purchase_rate}% Repeat</span>
          <span class="kpi-subtext">Retention rate</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Historical Avg CLV</span>
          <div class="kpi-icon-wrapper"><i data-lucide="award"></i></div>
        </div>
        <div class="kpi-value">${Format.currency(summary.average_clv_historical)}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Historical lifetime value</span></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">3-Year Projected CLV</span>
          <div class="kpi-icon-wrapper"><i data-lucide="trending-up"></i></div>
        </div>
        <div class="kpi-value">${Format.currency(summary.projected_clv_3yr)}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Predictive future value</span></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Purchase Frequency</span>
          <div class="kpi-icon-wrapper"><i data-lucide="repeat"></i></div>
        </div>
        <div class="kpi-value">${summary.average_purchase_frequency}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Avg orders / customer</span></div>
      </div>
    `;

    if (window.lucide) lucide.createIcons();
  },

  renderCohortChart(cohort) {
    if (!cohort || !cohort.labels) return;

    ChartManager.createBarChart('customer-cohort-chart', cohort.labels, [
      {
        label: 'New Customers (₹)',
        data: cohort.new_revenue,
        backgroundColor: 'rgba(99, 102, 241, 0.85)',
        stack: 'combined'
      },
      {
        label: 'Returning Customers (₹)',
        data: cohort.returning_revenue,
        backgroundColor: 'rgba(16, 185, 129, 0.85)',
        stack: 'combined'
      }
    ], {
      scales: {
        x: { stacked: true },
        y: {
          stacked: true,
          ticks: { callback: (v) => Format.compact(v) }
        }
      }
    });
  },

  renderFrequencyChart(dist) {
    if (!dist || !dist.labels) return;

    ChartManager.createBarChart('customer-frequency-chart', dist.labels, [
      {
        label: 'Customers',
        data: dist.counts,
        backgroundColor: ChartManager.colors.palette.slice(0, dist.labels.length),
        borderRadius: 6
      }
    ]);
  },

  renderRfmSegments(segments) {
    const container = document.getElementById('rfm-segment-cards');
    if (!container || !segments) return;

    const badgeClass = (name) => {
      if (name.includes('Champion')) return 'badge-champion';
      if (name.includes('Loyal')) return 'badge-loyal';
      if (name.includes('Risk') || name.includes("Can't Lose")) return 'badge-risk';
      if (name.includes('Hibernating')) return 'badge-hibernating';
      return 'badge-potential';
    };

    container.innerHTML = segments.slice(0, 6).map(s => `
      <div style="background: var(--bg-tertiary); border: 1px solid var(--border-medium); border-radius: 8px; padding: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span class="badge ${badgeClass(s.segment)}" style="font-size: 0.8rem;">${s.segment}</span>
          <span style="font-size: 0.8rem; color: var(--text-muted);">${s.customer_count} cust. (${s.customer_percentage}%)</span>
        </div>
        <div style="font-size: 1.4rem; font-weight: 800; color: var(--text-primary);">${Format.currency(s.total_revenue)}</div>
        <div style="font-size: 0.75rem; color: var(--text-secondary); display: grid; grid-template-columns: 1fr 1fr; gap: 0.25rem;">
          <div>Avg Recency: <b>${s.avg_recency_days}d</b></div>
          <div>Avg Orders: <b>${s.avg_frequency}</b></div>
          <div>Avg Spend: <b>${Format.currency(s.avg_monetary)}</b></div>
          <div>Revenue Share: <b>${s.revenue_percentage}%</b></div>
        </div>
      </div>
    `).join('');
  },

  populateTable(customers) {
    const tbody = document.querySelector('#high-value-customers-table tbody');
    if (!tbody || !customers) return;

    if (customers.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No customers found matching search.</td></tr>`;
      return;
    }

    const badgeClass = (name) => {
      if (name.includes('Champion')) return 'badge-champion';
      if (name.includes('Loyal')) return 'badge-loyal';
      if (name.includes('Risk') || name.includes("Can't Lose")) return 'badge-risk';
      return 'badge-potential';
    };

    tbody.innerHTML = customers.map(c => `
      <tr>
        <td>
          <div style="font-weight: 600; color: var(--text-primary);">${c.customer_name}</div>
          <div style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">${c.customer_id} &bull; ${c.region}</div>
        </td>
        <td><span class="badge" style="background: rgba(255,255,255,0.06);">${c.segment}</span></td>
        <td><span class="badge ${badgeClass(c.rfm_segment)}">${c.rfm_segment}</span></td>
        <td style="font-weight: 700; color: var(--text-primary);">${Format.currency(c.total_spend)}</td>
        <td>${c.total_orders}</td>
        <td>${Format.currency(c.aov)}</td>
        <td>${c.recency_days} days ago</td>
        <td><span style="color: var(--accent-cyan); font-weight: 500;">${c.favorite_category}</span></td>
      </tr>
    `).join('');
  },

  filterTable(query) {
    if (!query) {
      this.populateTable(this.highValueCustomers);
      return;
    }
    const q = query.toLowerCase();
    const filtered = this.highValueCustomers.filter(c =>
      c.customer_name.toLowerCase().includes(q) ||
      c.customer_id.toLowerCase().includes(q) ||
      c.rfm_segment.toLowerCase().includes(q) ||
      c.favorite_category.toLowerCase().includes(q)
    );
    this.populateTable(filtered);
  }
};
