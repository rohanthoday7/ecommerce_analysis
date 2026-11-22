/**
 * Product Analytics & Comparison Module Renderer
 */

const ProductModule = {
  selectedComparisonIds: [],
  catalogList: [],

  async render(container, filters) {
    container.innerHTML = `
      <div class="kpi-grid" id="product-kpis">
        <div class="kpi-card"><div class="kpi-title">Loading Product Metrics...</div></div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">Pareto 80/20 Catalog Revenue Concentration</div>
            <div class="card-desc">Cumulative revenue distribution across product catalog ranking</div>
          </div>
        </div>
        <div class="chart-container" style="height: 300px;">
          <canvas id="product-pareto-chart"></canvas>
        </div>
      </div>

      <!-- Multi-Product Comparison Engine -->
      <div class="card" style="border-left: 4px solid var(--accent-violet);">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">Side-by-Side Product Comparison Engine</div>
            <div class="card-desc">Benchmark unit velocity, margin profiles, and demand trajectory</div>
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <select id="product-selector-1" class="filter-select filter-group" onchange="ProductModule.handleCompareChange()"></select>
            <select id="product-selector-2" class="filter-select filter-group" onchange="ProductModule.handleCompareChange()"></select>
          </div>
        </div>
        <div id="product-comparison-grid" class="grid-2">
          <div style="color: var(--text-muted); padding: 1rem;">Loading product comparison...</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Top 10 Best Sellers (By Revenue)</div>
              <div class="card-desc">Hero revenue contributors</div>
            </div>
          </div>
          <div class="table-wrapper">
            <table class="data-table" id="top-rev-products-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Revenue</th>
                  <th>Units</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Bottom 10 Slowest Movers</div>
              <div class="card-desc">Lowest volume/revenue SKUs requiring review</div>
            </div>
          </div>
          <div class="table-wrapper">
            <table class="data-table" id="bottom-products-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Revenue</th>
                  <th>Units</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">Category & Sub-Category Product Hierarchy</div>
            <div class="card-desc">Departmental volume, catalog breadth, and gross revenue</div>
          </div>
        </div>
        <div class="table-wrapper">
          <table class="data-table" id="product-hierarchy-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Sub-Category</th>
                <th>Active SKUs</th>
                <th>Total Volume</th>
                <th>Revenue</th>
                <th>Revenue Share</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    `;

    try {
      const data = await API.getProductAnalytics(filters, this.selectedComparisonIds);
      this.catalogList = data.catalog_list || [];
      this.populateKPIs(data.summary);
      this.renderParetoChart(data.pareto_analysis);
      this.populateSelectors(data.catalog_list);
      this.renderComparisonCards(data.comparison);
      this.populateRankings(data.top_products_revenue, data.bottom_products);
      this.populateHierarchy(data.category_matrix);
    } catch (err) {
      container.innerHTML = `<div class="card" style="color: var(--accent-rose); padding: 2rem;">Error loading product analytics: ${err.message}</div>`;
    }
  },

  populateKPIs(summary) {
    const kpiContainer = document.getElementById('product-kpis');
    if (!kpiContainer || !summary) return;

    kpiContainer.innerHTML = `
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Active Catalog Breadth</span>
          <div class="kpi-icon-wrapper"><i data-lucide="layers"></i></div>
        </div>
        <div class="kpi-value">${Format.number(summary.total_products)}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Distinct product SKUs</span></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Total Units Shipped</span>
          <div class="kpi-icon-wrapper"><i data-lucide="package"></i></div>
        </div>
        <div class="kpi-value">${Format.number(summary.total_quantity)}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Aggregated unit volume</span></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Catalog Gross Revenue</span>
          <div class="kpi-icon-wrapper"><i data-lucide="dollar-sign"></i></div>
        </div>
        <div class="kpi-value">${Format.currency(summary.total_revenue)}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Product sales total</span></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">80/20 Pareto Threshold</span>
          <div class="kpi-icon-wrapper"><i data-lucide="pie-chart"></i></div>
        </div>
        <div class="kpi-value" style="font-size: 1.25rem; line-height: 1.35; color: var(--accent-amber);">
          ${summary.pareto_summary || 'Top 20% generate 80%'}
        </div>
        <div class="kpi-footer"><span class="kpi-subtext">Revenue concentration</span></div>
      </div>
    `;

    if (window.lucide) lucide.createIcons();
  },

  renderParetoChart(pareto) {
    if (!pareto || !pareto.product_rank_pct) return;

    ChartManager.createLineChart('product-pareto-chart', pareto.product_rank_pct, [
      {
        label: 'Cumulative Revenue %',
        data: pareto.cumulative_revenue_pct,
        borderColor: ChartManager.colors.indigo,
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        fill: true,
        tension: 0.25
      },
      {
        label: '80% Benchmark Line',
        data: pareto.product_rank_pct.map(() => 80),
        borderColor: ChartManager.colors.rose,
        borderDash: [6, 6],
        pointRadius: 0
      }
    ], {
      scales: {
        x: {
          title: { display: true, text: '% of Product Catalog (Ranked by Sales)', color: '#64748b' },
          ticks: { callback: (v) => `${v}%` }
        },
        y: {
          title: { display: true, text: 'Cumulative Revenue %', color: '#64748b' },
          max: 100,
          ticks: { callback: (v) => `${v}%` }
        }
      }
    });
  },

  populateSelectors(catalog) {
    const sel1 = document.getElementById('product-selector-1');
    const sel2 = document.getElementById('product-selector-2');
    if (!sel1 || !sel2 || !catalog || catalog.length === 0) return;

    const optionsHtml = catalog.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    sel1.innerHTML = optionsHtml;
    sel2.innerHTML = optionsHtml;

    if (catalog.length > 1) {
      sel1.selectedIndex = 0;
      sel2.selectedIndex = 1;
      this.selectedComparisonIds = [catalog[0].id, catalog[1].id];
    }
  },

  async handleCompareChange() {
    const sel1 = document.getElementById('product-selector-1');
    const sel2 = document.getElementById('product-selector-2');
    if (!sel1 || !sel2) return;

    this.selectedComparisonIds = [sel1.value, sel2.value];
    const data = await API.getProductAnalytics(State.filters, this.selectedComparisonIds);
    this.renderComparisonCards(data.comparison);
  },

  renderComparisonCards(comparison) {
    const container = document.getElementById('product-comparison-grid');
    if (!container || !comparison || comparison.length === 0) return;

    container.innerHTML = comparison.map((p, idx) => `
      <div style="background: var(--bg-tertiary); border: 1px solid var(--border-medium); border-radius: 8px; padding: 1.25rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
          <div>
            <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--accent-primary); font-weight: 700;">${p.category} &bull; ${p.sub_category}</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary); margin-top: 2px;">${p.product_name}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-mono);">${p.product_id}</div>
          </div>
          <div style="font-size: 1.3rem; font-weight: 800; color: var(--text-primary);">${Format.currency(p.revenue)}</div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; background: var(--bg-card); padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem;">
          <div>
            <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Units Sold</div>
            <div style="font-size: 1rem; font-weight: 700; color: #fff;">${Format.number(p.quantity)}</div>
          </div>
          <div>
            <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Orders</div>
            <div style="font-size: 1rem; font-weight: 700; color: #fff;">${Format.number(p.orders)}</div>
          </div>
          <div>
            <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Avg Price</div>
            <div style="font-size: 1rem; font-weight: 700; color: #fff;">${Format.currency(p.avg_price)}</div>
          </div>
        </div>

        <div style="height: 120px; position: relative;">
          <canvas id="compare-chart-${idx}"></canvas>
        </div>
      </div>
    `).join('');

    // Render sparkline demand trends for each product in comparison
    comparison.forEach((p, idx) => {
      const dt = p.demand_trend || {};
      ChartManager.createLineChart(`compare-chart-${idx}`, dt.labels || [], [
        {
          label: 'Monthly Sales (₹)',
          data: dt.revenue || [],
          borderColor: idx === 0 ? ChartManager.colors.indigo : ChartManager.colors.emerald,
          backgroundColor: idx === 0 ? 'rgba(99, 102, 241, 0.1)' : 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.3
        }
      ], {
        plugins: { legend: { display: false } },
        scales: {
          x: { display: false },
          y: { ticks: { callback: (v) => Format.compact(v) } }
        }
      });
    });
  },

  populateRankings(topProds, bottomProds) {
    const topTbody = document.querySelector('#top-rev-products-table tbody');
    const bottomTbody = document.querySelector('#bottom-products-table tbody');

    if (topTbody && topProds) {
      topTbody.innerHTML = topProds.map(p => `
        <tr>
          <td>
            <div style="font-weight: 600; color: var(--text-primary);">${p.product_name}</div>
            <div style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">${p.product_id}</div>
          </td>
          <td><span class="badge" style="background: rgba(255,255,255,0.06);">${p.category}</span></td>
          <td style="font-weight: 700; color: var(--text-primary);">${Format.currency(p.revenue)}</td>
          <td>${Format.number(p.quantity)}</td>
        </tr>
      `).join('');
    }

    if (bottomTbody && bottomProds) {
      bottomTbody.innerHTML = bottomProds.map(p => `
        <tr>
          <td>
            <div style="font-weight: 600; color: var(--text-primary);">${p.product_name}</div>
            <div style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">${p.product_id}</div>
          </td>
          <td><span class="badge" style="background: rgba(255,255,255,0.06);">${p.category}</span></td>
          <td style="font-weight: 700; color: var(--text-primary);">${Format.currency(p.revenue)}</td>
          <td>${Format.number(p.quantity)}</td>
        </tr>
      `).join('');
    }
  },

  populateHierarchy(matrix) {
    const tbody = document.querySelector('#product-hierarchy-table tbody');
    if (!tbody || !matrix) return;

    tbody.innerHTML = matrix.map(m => `
      <tr>
        <td style="font-weight: 600; color: var(--text-primary);">${m.category}</td>
        <td>${m.sub_category}</td>
        <td>${m.products_count}</td>
        <td>${Format.number(m.quantity)}</td>
        <td style="font-weight: 700; color: var(--text-primary);">${Format.currency(m.revenue)}</td>
        <td>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>${m.share}%</span>
            <div style="flex: 1; max-width: 60px; height: 5px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden;">
              <div style="width: ${m.share}%; height: 100%; background: var(--accent-violet);"></div>
            </div>
          </div>
        </td>
      </tr>
    `).join('');
  }
};
