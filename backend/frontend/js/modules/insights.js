/**
 * Automated Business Intelligence & Insights Module Renderer
 */

const InsightsModule = {
  allInsights: [],

  async render(container, filters) {
    container.innerHTML = `
      <div class="card" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.05) 100%); border-color: rgba(99, 102, 241, 0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #fff;">Automated Diagnostic & Strategic Intelligence</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 2px;">
              Empirical pattern recognition engine diagnosing catalog concentration, customer retention multipliers, margin dilution, and seasonality spikes.
            </div>
          </div>
          <div class="preset-pills">
            <button class="pill-btn active" onclick="InsightsModule.filterCategory('all')">All Findings</button>
            <button class="pill-btn" onclick="InsightsModule.filterCategory('warning')">Risks & Alerts</button>
            <button class="pill-btn" onclick="InsightsModule.filterCategory('positive')">Growth Drivers</button>
            <button class="pill-btn" onclick="InsightsModule.filterCategory('info')">Operational</button>
          </div>
        </div>
      </div>

      <div class="insights-grid" id="insights-container">
        <div class="card"><div class="card-desc">Analyzing dataset patterns...</div></div>
      </div>
    `;

    try {
      this.allInsights = await API.getInsights(filters);
      this.renderInsightCards(this.allInsights);
    } catch (err) {
      container.innerHTML = `<div class="card" style="color: var(--accent-rose); padding: 2rem;">Error computing business insights: ${err.message}</div>`;
    }
  },

  renderInsightCards(insights) {
    const container = document.getElementById('insights-container');
    if (!container) return;

    if (!insights || insights.length === 0) {
      container.innerHTML = `<div class="card" style="padding: 2rem; color: var(--text-muted); text-align: center;">No anomalous patterns detected for current filters.</div>`;
      return;
    }

    container.innerHTML = insights.map(ins => `
      <div class="insight-card ${ins.type || 'info'}">
        <div class="insight-top">
          <span class="insight-category">${ins.category}</span>
          <span class="badge ${ins.type === 'warning' ? 'badge-risk' : (ins.type === 'positive' ? 'badge-champion' : 'badge-potential')}">${ins.badge}</span>
        </div>

        <div class="insight-title">${ins.title}</div>

        <div class="insight-section">
          <span class="insight-label">1. Finding</span>
          <div class="insight-finding">${ins.finding}</div>
        </div>

        <div class="insight-section">
          <span class="insight-label">2. Supporting Data</span>
          <div class="insight-data-box">${ins.supporting_data}</div>
        </div>

        <div class="insight-section">
          <span class="insight-label">3. Business Implication</span>
          <div class="insight-implication">${ins.business_implication}</div>
        </div>

        <div class="insight-section">
          <span class="insight-label">4. Recommended Action</span>
          <div class="insight-recommendation">
            <b>Action Plan:</b> ${ins.recommended_action}
          </div>
        </div>
      </div>
    `).join('');
  },

  filterCategory(type) {
    document.querySelectorAll('.preset-pills .pill-btn').forEach(btn => {
      btn.classList.toggle('active', btn.textContent.toLowerCase().includes(type) || (type === 'all' && btn.textContent.includes('All')));
    });

    if (type === 'all') {
      this.renderInsightCards(this.allInsights);
    } else {
      const filtered = this.allInsights.filter(ins => ins.type === type);
      this.renderInsightCards(filtered);
    }
  }
};
