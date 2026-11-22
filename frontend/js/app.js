/**
 * Main Application Orchestrator
 * Controls navigation routing, filter bar bindings, toast notifications, and module lifecycle.
 */

const App = {
  async init() {
    console.log("Initializing Enterprise Analytics Platform...");

    // 1. Setup Navigation Event Listeners
    this.setupNavigation();

    // 2. Setup Global Filter Bar Listeners
    this.setupFilters();

    // 3. Setup State Subscriptions
    State.subscribe((event, data) => {
      if (event === 'module_changed') {
        this.switchView(data);
      } else if (event === 'filters_changed') {
        this.renderActiveModule();
      } else if (event === 'dataset_changed') {
        this.updateDatasetBadge(data);
        this.updateFilterDropdowns(data.filter_options);
        this.renderActiveModule();
      }
    });

    // 4. Load Initial Dataset Status
    try {
      const status = await API.getDatasetStatus();
      if (status.loaded) {
        State.setDatasetStatus(status);
      } else {
        await API.loadSampleDataset();
        const reloaded = await API.getDatasetStatus();
        State.setDatasetStatus(reloaded);
      }
    } catch (err) {
      console.error("Failed to initialize dataset:", err);
      this.showToast("Failed to load initial dataset", "error");
    }

    // 5. Initial Render
    this.renderActiveModule();
  },

  setupNavigation() {
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const moduleName = item.getAttribute('data-module');
        if (moduleName) {
          document.querySelectorAll('.sidebar-nav .nav-item').forEach(n => n.classList.remove('active'));
          item.classList.add('active');
          State.setModule(moduleName);
        }
      });
    });
  },

  setupFilters() {
    const startInput = document.getElementById('filter-start-date');
    const endInput = document.getElementById('filter-end-date');
    const catSelect = document.getElementById('filter-category');
    const regSelect = document.getElementById('filter-region');
    const resetBtn = document.getElementById('btn-reset-filters');

    if (startInput) {
      startInput.addEventListener('change', () => {
        State.setFilters({ start_date: startInput.value, preset: 'custom' });
        this.updatePresetButtons('custom');
      });
    }

    if (endInput) {
      endInput.addEventListener('change', () => {
        State.setFilters({ end_date: endInput.value, preset: 'custom' });
        this.updatePresetButtons('custom');
      });
    }

    if (catSelect) {
      catSelect.addEventListener('change', () => {
        State.setFilters({ category: catSelect.value });
      });
    }

    if (regSelect) {
      regSelect.addEventListener('change', () => {
        State.setFilters({ region: regSelect.value });
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        State.resetFilters();
        this.syncFilterInputs();
        this.updatePresetButtons('all');
        this.showToast('Filters reset to default range.', 'info');
      });
    }
  },

  updatePresetButtons(activePreset) {
    document.querySelectorAll('.header-presets .pill-btn').forEach(btn => {
      const p = btn.getAttribute('data-preset');
      btn.classList.toggle('active', p === activePreset);
    });
  },

  handlePreset(preset) {
    const opts = State.filterOptions;
    if (!opts || !opts.max_date) return;

    const maxDate = new Date(opts.max_date);
    let sDate = null;
    const eDate = opts.max_date;

    if (preset === 'all') {
      sDate = opts.min_date;
    } else if (preset === '30d') {
      const d = new Date(maxDate);
      d.setDate(d.getDate() - 30);
      sDate = d.toISOString().split('T')[0];
    } else if (preset === '90d') {
      const d = new Date(maxDate);
      d.setDate(d.getDate() - 90);
      sDate = d.toISOString().split('T')[0];
    } else if (preset === 'ytd') {
      sDate = `${maxDate.getFullYear()}-01-01`;
    }

    this.updatePresetButtons(preset);

    const startInput = document.getElementById('filter-start-date');
    const endInput = document.getElementById('filter-end-date');
    if (startInput) startInput.value = sDate;
    if (endInput) endInput.value = eDate;

    State.setFilters({ start_date: sDate, end_date: eDate, preset: preset });
  },

  syncFilterInputs() {
    const startInput = document.getElementById('filter-start-date');
    const endInput = document.getElementById('filter-end-date');
    const catSelect = document.getElementById('filter-category');
    const regSelect = document.getElementById('filter-region');

    if (startInput) startInput.value = State.filters.start_date || '';
    if (endInput) endInput.value = State.filters.end_date || '';
    if (catSelect) catSelect.value = State.filters.category || 'all';
    if (regSelect) regSelect.value = State.filters.region || 'all';
  },

  updateFilterDropdowns(options) {
    if (!options) return;

    const catSelect = document.getElementById('filter-category');
    const regSelect = document.getElementById('filter-region');

    if (catSelect) {
      const current = State.filters.category;
      catSelect.innerHTML = `<option value="all">All Categories</option>` +
        (options.categories || []).map(c => `<option value="${c}" ${c === current ? 'selected' : ''}>${c}</option>`).join('');
    }

    if (regSelect) {
      const current = State.filters.region;
      regSelect.innerHTML = `<option value="all">All Regions</option>` +
        (options.regions || []).map(r => `<option value="${r}" ${r === current ? 'selected' : ''}>${r}</option>`).join('');
    }

    this.syncFilterInputs();
  },

  updateDatasetBadge(status) {
    const nameEl = document.getElementById('status-dataset-name');
    const recsEl = document.getElementById('status-dataset-records');
    if (nameEl) nameEl.textContent = status.name || 'sample_ecommerce.csv';
    if (recsEl) recsEl.textContent = `${Format.number(status.total_rows)} transactions`;
  },

  switchView(moduleName) {
    document.querySelectorAll('.module-view').forEach(view => view.classList.remove('active'));
    const target = document.getElementById(`view-${moduleName}`);
    if (target) {
      target.classList.add('active');
    }

    // Update Header Page Title
    const titles = {
      'executive': { title: 'Executive Performance Dashboard', desc: 'Holistic C-suite enterprise health overview and high-level KPIs' },
      'sales': { title: 'Advanced Sales Analytics', desc: 'Granular time-series analysis, MoM growth rates, and seasonal curves' },
      'products': { title: 'Product Catalog Intelligence', desc: 'Pareto 80/20 concentration, hero items, and side-by-side comparison' },
      'customers': { title: 'Customer Lifetime & RFM Segmentation', desc: 'Behavioral customer cohorts, retention dynamics, and VIP accounts' },
      'regional': { title: 'Regional & Geospatial Analytics', desc: 'Territory volume, market penetration maps, and state-level benchmarking' },
      'insights': { title: 'Automated Business Insights & Intelligence', desc: 'Algorithmic pattern recognition and strategic diagnostic findings' },
      'data-mgmt': { title: 'Data Management & Preprocessing Studio', desc: 'Dataset ingestion, data quality scoring, schema mapping, and exports' }
    };

    const header = titles[moduleName] || titles['executive'];
    const titleEl = document.getElementById('page-main-title');
    const descEl = document.getElementById('page-main-desc');
    if (titleEl) titleEl.textContent = header.title;
    if (descEl) descEl.textContent = header.desc;

    this.renderActiveModule();

    // If switching to regional, invalidate map size after transition
    if (moduleName === 'regional' && window.RegionalModule && RegionalModule.mapInstance) {
      setTimeout(() => {
        try {
          RegionalModule.mapInstance.invalidateSize();
        } catch (e) {}
      }, 300);
    }
  },

  renderActiveModule() {
    const mod = State.currentModule;
    const container = document.getElementById(`view-${mod}`);
    if (!container) return;

    if (mod === 'executive') ExecutiveModule.render(container, State.filters);
    else if (mod === 'sales') SalesModule.render(container, State.filters);
    else if (mod === 'products') ProductModule.render(container, State.filters);
    else if (mod === 'customers') CustomerModule.render(container, State.filters);
    else if (mod === 'regional') RegionalModule.render(container, State.filters);
    else if (mod === 'insights') InsightsModule.render(container, State.filters);
    else if (mod === 'data-mgmt') DataMgmtModule.render(container);
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';

    let icon = 'info';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'alert-triangle';

    toast.innerHTML = `
      <i data-lucide="${icon}" style="color: ${type === 'success' ? 'var(--accent-emerald)' : (type === 'error' ? 'var(--accent-rose)' : 'var(--accent-primary)')}"></i>
      <span>${message}</span>
    `;

    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  },

  openExportReportModal() {
    window.print();
  }
};

window.addEventListener('DOMContentLoaded', () => {
  App.init();
});
