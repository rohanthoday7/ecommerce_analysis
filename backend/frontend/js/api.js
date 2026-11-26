/**
 * API Client for Enterprise Analytics Platform
 * Wraps all backend endpoints with automatic filter parameter injection.
 */

const API = {
  baseUrl: window.location.origin,

  /** Build query string from current active filters */
  buildQueryString(filters = {}, extra = {}) {
    const params = new URLSearchParams();
    const merged = { ...filters, ...extra };
    
    for (const [key, value] of Object.entries(merged)) {
      if (value !== null && value !== undefined && value !== '' && value !== 'all') {
        params.append(key, value);
      }
    }
    const qs = params.toString();
    return qs ? `?${qs}` : '';
  },

  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, options);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed with status ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  // Dataset Management
  getDatasetStatus() {
    return this.request('/api/dataset/status');
  },

  getDatasetProfile() {
    return this.request('/api/dataset/profile');
  },

  getDatasetPreview(page = 1, pageSize = 25, search = '') {
    const qs = this.buildQueryString({}, { page, page_size: pageSize, search });
    return this.request(`/api/dataset/preview${qs}`);
  },

  async uploadDataset(file) {
    const formData = new FormData();
    formData.append('file', file);
    return this.request('/api/dataset/upload', {
      method: 'POST',
      body: formData
    });
  },

  loadSampleDataset() {
    return this.request('/api/dataset/load-sample', { method: 'POST' });
  },

  remapDataset(mapping) {
    return this.request('/api/dataset/remap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(mapping)
    });
  },

  preprocessDataset(options) {
    const formData = new FormData();
    formData.append('drop_duplicates', options.dropDuplicates);
    formData.append('impute_missing', options.imputeMissing);
    formData.append('remove_negative_sales', options.removeNegativeSales);
    return this.request('/api/dataset/preprocess', {
      method: 'POST',
      body: formData
    });
  },

  // Analytics
  getFilters() {
    return this.request('/api/analytics/filters');
  },

  getExecutiveAnalytics(filters) {
    return this.request(`/api/analytics/executive${this.buildQueryString(filters)}`);
  },

  getSalesAnalytics(filters) {
    return this.request(`/api/analytics/sales${this.buildQueryString(filters)}`);
  },

  getProductAnalytics(filters, compareIds = null) {
    const extra = compareIds ? { compare: compareIds.join(',') } : {};
    return this.request(`/api/analytics/products${this.buildQueryString(filters, extra)}`);
  },

  getCustomerAnalytics(filters) {
    return this.request(`/api/analytics/customers${this.buildQueryString(filters)}`);
  },

  getRegionalAnalytics(filters) {
    return this.request(`/api/analytics/regional${this.buildQueryString(filters)}`);
  },

  getInsights(filters) {
    return this.request(`/api/analytics/insights${this.buildQueryString(filters)}`);
  }
};
