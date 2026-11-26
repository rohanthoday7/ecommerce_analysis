/**
 * Regional & Geospatial Analytics Module Renderer
 * Embeds Leaflet map with interactive sales bubbles and regional growth tracking.
 */

const RegionalModule = {
  mapInstance: null,

  async render(container, filters) {
    container.innerHTML = `
      <div class="kpi-grid" id="regional-kpis">
        <div class="kpi-card"><div class="kpi-title">Loading Regional Data...</div></div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">Geospatial Market Penetration Map</div>
            <div class="card-desc">Interactive geographic distribution of revenue, transaction density, and AOV</div>
          </div>
        </div>
        <div id="regional-map"></div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Territory Revenue Comparison</div>
              <div class="card-desc">Sales volume and customer base by operational zone</div>
            </div>
          </div>
          <div class="chart-container" style="height: 280px;">
            <canvas id="regional-territory-chart"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Quarterly Regional Growth Trajectory</div>
              <div class="card-desc">Comparative chronological performance across geographic zones</div>
            </div>
          </div>
          <div class="chart-container" style="height: 280px;">
            <canvas id="regional-growth-chart"></canvas>
          </div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">State-Level Performance Breakdown</div>
              <div class="card-desc">Ranked by top-line revenue contribution</div>
            </div>
          </div>
          <div class="table-wrapper" style="max-height: 400px; overflow-y: auto;">
            <table class="data-table" id="state-performance-table">
              <thead>
                <tr>
                  <th>State</th>
                  <th>Region</th>
                  <th>Revenue</th>
                  <th>Share</th>
                  <th>Orders</th>
                  <th>AOV</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Top 15 Metro Markets (Cities)</div>
              <div class="card-desc">Highest volume municipal sales hubs</div>
            </div>
          </div>
          <div class="table-wrapper" style="max-height: 400px; overflow-y: auto;">
            <table class="data-table" id="city-performance-table">
              <thead>
                <tr>
                  <th>City</th>
                  <th>State</th>
                  <th>Region</th>
                  <th>Revenue</th>
                  <th>Orders</th>
                  <th>AOV</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>
      </div>
    `;

    try {
      const data = await API.getRegionalAnalytics(filters);
      this.populateKPIs(data.summary);
      this.renderMap(data.map_points);
      this.renderCharts(data);
      this.populateTables(data.states, data.cities);
    } catch (err) {
      container.innerHTML = `<div class="card" style="color: var(--accent-rose); padding: 2rem;">Error loading regional analytics: ${err.message}</div>`;
    }
  },

  populateKPIs(summary) {
    const kpiContainer = document.getElementById('regional-kpis');
    if (!kpiContainer || !summary) return;

    kpiContainer.innerHTML = `
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Active Territories</span>
          <div class="kpi-icon-wrapper"><i data-lucide="map"></i></div>
        </div>
        <div class="kpi-value">${summary.total_regions}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Geographic operating zones</span></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">States / Markets Served</span>
          <div class="kpi-icon-wrapper"><i data-lucide="navigation"></i></div>
        </div>
        <div class="kpi-value">${summary.total_states}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Distinct state jurisdictions</span></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Leading Region</span>
          <div class="kpi-icon-wrapper"><i data-lucide="compass"></i></div>
        </div>
        <div class="kpi-value" style="color: var(--accent-cyan); font-size: 1.5rem;">${summary.top_region_name}</div>
        <div class="kpi-footer">
          <span class="growth-badge growth-positive">${summary.top_region_share}% Share</span>
          <span class="kpi-subtext">${Format.currency(summary.top_region_revenue)}</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Metro Municipalities</span>
          <div class="kpi-icon-wrapper"><i data-lucide="map-pin"></i></div>
        </div>
        <div class="kpi-value">${summary.total_cities}</div>
        <div class="kpi-footer"><span class="kpi-subtext">Active commercial cities</span></div>
      </div>
    `;

    if (window.lucide) lucide.createIcons();
  },

  renderMap(points) {
    if (!window.L) return;

    // Clean up existing Leaflet map instance if re-rendering
    if (this.mapInstance) {
      try {
        this.mapInstance.off();
        this.mapInstance.remove();
      } catch (e) {
        console.warn('Map cleanup notice:', e);
      }
      this.mapInstance = null;
    }

    const mapEl = document.getElementById('regional-map');
    if (!mapEl) return;
    mapEl._leaflet_id = null; // Prevent "Map container is already initialized" error

    try {
      // Initialize map
      this.mapInstance = L.map('regional-map', {
        center: [39.0, -98.0],
        zoom: 4,
        scrollWheelZoom: false
      });

      // Dark Tile Layer (CartoDB Dark Matter)
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 18
      }).addTo(this.mapInstance);

      // Invalidate size to ensure tiles render immediately
      setTimeout(() => {
        if (this.mapInstance) {
          this.mapInstance.invalidateSize();
        }
      }, 250);

      if (!points || points.length === 0) {
        // Display notification on map when no coordinates mapped
        const info = L.control({ position: 'topright' });
        info.onAdd = function() {
          const div = L.DomUtil.create('div', 'map-info-badge');
          div.style.background = 'rgba(18, 24, 38, 0.9)';
          div.style.padding = '8px 12px';
          div.style.borderRadius = '6px';
          div.style.color = '#94a3b8';
          div.style.fontSize = '12px';
          div.style.border = '1px solid rgba(255,255,255,0.1)';
          div.innerHTML = 'Territory breakdown displayed in tables below.';
          return div;
        };
        info.addTo(this.mapInstance);
        return;
      }

      const maxRev = Math.max(...points.map(p => p.revenue), 1);
      const markers = [];

      points.forEach(pt => {
        // Radius scaled from 8px to 30px based on revenue
        const radius = 8 + (pt.revenue / maxRev) * 22;

        const circle = L.circleMarker([pt.lat, pt.lng], {
          radius: radius,
          fillColor: '#6366f1',
          color: '#a5b4fc',
          weight: 1.5,
          opacity: 0.95,
          fillOpacity: 0.6
        }).addTo(this.mapInstance);

        circle.bindPopup(`
          <div style="font-family: var(--font-sans); padding: 4px;">
            <div style="font-size: 1rem; font-weight: 800; color: #fff; margin-bottom: 2px;">${pt.name}</div>
            <div style="font-size: 0.75rem; color: var(--accent-primary); text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">${pt.region} Territory</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.78rem;">
              <div>Revenue: <b style="color: #fff;">${Format.currency(pt.revenue)}</b></div>
              <div>Orders: <b style="color: #fff;">${Format.number(pt.orders)}</b></div>
              <div>Customers: <b style="color: #fff;">${Format.number(pt.customers)}</b></div>
              <div>AOV: <b style="color: var(--accent-emerald);">${Format.currency(pt.aov)}</b></div>
            </div>
          </div>
        `);
        markers.push(circle);
      });

      if (markers.length > 1) {
        const group = L.featureGroup(markers);
        this.mapInstance.fitBounds(group.getBounds().pad(0.15));
      }
    } catch (err) {
      console.error('Error rendering Leaflet map:', err);
      mapEl.innerHTML = `<div style="padding: 2rem; color: var(--text-muted); text-align: center;">Geographic data visualized in the territory and state tables below.</div>`;
    }
  },

  renderCharts(data) {
    // 1. Territory Chart
    const regions = data.regions || [];
    ChartManager.createBarChart('regional-territory-chart', regions.map(r => r.region), [
      {
        label: 'Revenue (₹)',
        data: regions.map(r => r.revenue),
        backgroundColor: 'rgba(99, 102, 241, 0.85)',
        borderRadius: 6
      }
    ], {
      scales: {
        y: { ticks: { callback: (v) => Format.compact(v) } }
      }
    });

    // 2. Regional Growth
    const rg = data.regional_growth || {};
    const datasets = (rg.datasets || []).map((ds, idx) => ({
      label: ds.region,
      data: ds.revenue,
      borderColor: ChartManager.colors.palette[idx % ChartManager.colors.palette.length],
      tension: 0.3,
      fill: false
    }));

    ChartManager.createLineChart('regional-growth-chart', rg.labels || [], datasets, {
      scales: {
        y: { ticks: { callback: (v) => Format.compact(v) } }
      }
    });
  },

  populateTables(states, cities) {
    const stateTbody = document.querySelector('#state-performance-table tbody');
    const cityTbody = document.querySelector('#city-performance-table tbody');

    if (stateTbody && states) {
      stateTbody.innerHTML = states.map(s => `
        <tr>
          <td style="font-weight: 600; color: var(--text-primary);">${s.state}</td>
          <td><span class="badge" style="background: rgba(255,255,255,0.06);">${s.region}</span></td>
          <td style="font-weight: 700; color: var(--text-primary);">${Format.currency(s.revenue)}</td>
          <td>${s.rev_share}%</td>
          <td>${Format.number(s.orders)}</td>
          <td style="color: var(--accent-emerald); font-weight: 600;">${Format.currency(s.aov)}</td>
        </tr>
      `).join('');
    }

    if (cityTbody && cities) {
      cityTbody.innerHTML = cities.map(c => `
        <tr>
          <td style="font-weight: 600; color: var(--text-primary);">${c.city}</td>
          <td>${c.state}</td>
          <td><span class="badge" style="background: rgba(255,255,255,0.06);">${c.region}</span></td>
          <td style="font-weight: 700; color: var(--text-primary);">${Format.currency(c.revenue)}</td>
          <td>${Format.number(c.orders)}</td>
          <td style="color: var(--accent-emerald); font-weight: 600;">${Format.currency(c.aov)}</td>
        </tr>
      `).join('');
    }
  }
};
