/**
 * Reactive Application State Store
 * Manages active modules, global filters, dataset status, and listeners.
 */

const State = {
  currentModule: 'executive',
  
  filters: {
    start_date: null,
    end_date: null,
    category: 'all',
    region: 'all',
    segment: 'all',
    payment_method: 'all',
    preset: 'all'
  },

  datasetStatus: {
    loaded: false,
    name: '',
    total_rows: 0,
    health_score: 100,
    has_profit_data: false
  },

  currencySymbol: '₹',

  filterOptions: {
    min_date: null,
    max_date: null,
    categories: [],
    regions: [],
    segments: [],
    payment_methods: []
  },

  listeners: [],

  subscribe(fn) {
    this.listeners.push(fn);
  },

  notify(event, data) {
    for (const listener of this.listeners) {
      try {
        listener(event, data);
      } catch (err) {
        console.error('State listener error:', err);
      }
    }
  },

  setModule(moduleName) {
    this.currentModule = moduleName;
    this.notify('module_changed', moduleName);
  },

  setFilters(newFilters, triggerRefresh = true) {
    this.filters = { ...this.filters, ...newFilters };
    if (triggerRefresh) {
      this.notify('filters_changed', this.filters);
    }
  },

  resetFilters() {
    this.filters = {
      start_date: this.filterOptions.min_date,
      end_date: this.filterOptions.max_date,
      category: 'all',
      region: 'all',
      segment: 'all',
      payment_method: 'all',
      preset: 'all'
    };
    this.notify('filters_changed', this.filters);
  },

  setDatasetStatus(status) {
    this.datasetStatus = status;
    this.currencySymbol = status.currency_symbol || '₹';
    if (status.filter_options) {
      this.filterOptions = status.filter_options;
      // ALWAYS reset active date and category filters to the new dataset's actual bounds!
      this.filters.start_date = status.filter_options.min_date || null;
      this.filters.end_date = status.filter_options.max_date || null;
      this.filters.category = 'all';
      this.filters.region = 'all';
      this.filters.segment = 'all';
      this.filters.payment_method = 'all';
      this.filters.preset = 'all';
    }
    this.notify('dataset_changed', status);
  }
};
