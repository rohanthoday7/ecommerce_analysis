/**
 * Chart.js Enterprise Dark Theme Integration
 * Manages chart lifecycle, memory cleanup, and custom styling.
 */

const ChartManager = {
  instances: {},

  colors: {
    indigo: '#6366f1',
    violet: '#8b5cf6',
    emerald: '#10b981',
    rose: '#f43f5e',
    amber: '#f59e0b',
    cyan: '#06b6d4',
    blue: '#3b82f6',
    slate: '#64748b',
    palette: [
      '#6366f1', '#10b981', '#06b6d4', '#f59e0b', '#ec4899',
      '#8b5cf6', '#3b82f6', '#14b8a6', '#f43f5e', '#a855f7'
    ]
  },

  destroy(id) {
    if (this.instances[id]) {
      this.instances[id].destroy();
      delete this.instances[id];
    }
  },

  destroyAll() {
    for (const id of Object.keys(this.instances)) {
      this.destroy(id);
    }
  },

  getDefaultOptions(overrides = {}) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: '#94a3b8',
            font: { family: "'Inter', sans-serif", size: 12 },
            usePointStyle: true,
            boxWidth: 8
          }
        },
        tooltip: {
          backgroundColor: '#161c2d',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(255, 255, 255, 0.12)',
          borderWidth: 1,
          padding: 10,
          cornerRadius: 6,
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
          titleFont: { weight: 'bold', size: 12 },
          bodyFont: { size: 12 }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)', borderColor: 'transparent' },
          ticks: { color: '#64748b', font: { size: 11 } }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)', borderColor: 'transparent' },
          ticks: { color: '#64748b', font: { size: 11 } }
        }
      },
      ...overrides
    };
  },

  createLineChart(canvasId, labels, datasets, options = {}) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const chartOptions = this.getDefaultOptions(options);

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: { labels, datasets },
      options: chartOptions
    });
    return this.instances[canvasId];
  },

  createBarChart(canvasId, labels, datasets, options = {}) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const chartOptions = this.getDefaultOptions(options);

    this.instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: { labels, datasets },
      options: chartOptions
    });
    return this.instances[canvasId];
  },

  createDoughnutChart(canvasId, labels, data, options = {}) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const baseOpts = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: '#94a3b8',
            font: { family: "'Inter', sans-serif", size: 11 },
            usePointStyle: true,
            boxWidth: 8
          }
        },
        tooltip: {
          backgroundColor: '#161c2d',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(255, 255, 255, 0.12)',
          borderWidth: 1,
          padding: 10,
          cornerRadius: 6
        }
      },
      cutout: '72%',
      ...options
    };

    this.instances[canvasId] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: this.colors.palette.slice(0, labels.length),
          borderColor: '#101522',
          borderWidth: 2,
          hoverOffset: 4
        }]
      },
      options: baseOpts
    });
    return this.instances[canvasId];
  }
};

// Formatting Utilities
const Format = {
  currency(val) {
    const sym = (typeof State !== 'undefined' && State.currencySymbol) ? State.currencySymbol : '₹';
    if (val === null || val === undefined || isNaN(val)) return `${sym}0.00`;
    const num = Number(val);
    const formatted = Math.abs(num).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
    return num < 0 ? `-${sym}${formatted}` : `${sym}${formatted}`;
  },

  number(val) {
    if (val === null || val === undefined || isNaN(val)) return '0';
    return new Intl.NumberFormat('en-US').format(val);
  },

  percent(val) {
    if (val === null || val === undefined || isNaN(val)) return '0.0%';
    return `${val > 0 ? '+' : ''}${Number(val).toFixed(1)}%`;
  },

  compact(val) {
    const sym = (typeof State !== 'undefined' && State.currencySymbol) ? State.currencySymbol : '₹';
    if (val === null || val === undefined || isNaN(val)) return `${sym}0`;
    const formatted = new Intl.NumberFormat('en-US', { notation: 'compact', compactDisplay: 'short' }).format(val);
    return `${sym}${formatted}`;
  }
};
