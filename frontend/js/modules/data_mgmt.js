/**
 * Data Management & Preprocessing Studio Module Renderer
 */

const DataMgmtModule = {
  currentPage: 1,
  pageSize: 15,
  searchQuery: '',
  profileData: null,
  previewData: null,

  async render(container) {
    container.innerHTML = `
      <div class="grid-2">
        <!-- Dataset Upload & Reset -->
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Upload Dataset (CSV or Excel)</div>
              <div class="card-desc">Ingest custom e-commerce transaction data (.csv, .xlsx, .xls, .tsv)</div>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <button class="btn btn-primary btn-sm" onclick="State.setModule('executive')">📊 View Dashboard →</button>
              <button class="btn btn-outline btn-sm" onclick="DataMgmtModule.resetSample()">Reset Sample</button>
            </div>
          </div>

          <div class="upload-dropzone" id="upload-dropzone" onclick="document.getElementById('file-upload-input').click()">
            <input type="file" id="file-upload-input" accept=".csv,.xlsx,.xls,.tsv,.txt" style="display: none;" onchange="DataMgmtModule.handleFileUpload(this.files[0])">
            <div class="dropzone-icon"><i data-lucide="upload-cloud"></i></div>
            <div style="font-weight: 700; color: #fff;">Drop files here or click to browse</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">Supports CSV, Excel (XLSX, XLS), TSV up to 50MB</div>
          </div>
        </div>

        <!-- Dataset Health Audit -->
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-title">Dataset Quality Health Audit</div>
              <div class="card-desc">Automatic integrity profiling, missing value density, and duplicates</div>
            </div>
          </div>

          <div id="health-audit-content" style="display: flex; flex-direction: column; gap: 1rem;">
            <div style="color: var(--text-muted);">Evaluating dataset health...</div>
          </div>
        </div>
      </div>

      <!-- Preprocessing Pipeline Controls -->
      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">Data Preprocessing & Cleaning Engine</div>
            <div class="card-desc">Execute genuine data hygiene and transformation routines</div>
          </div>
          <div style="display: flex; gap: 0.75rem;">
            <a href="/api/dataset/export?format=csv" class="btn btn-outline btn-sm"><i data-lucide="download"></i> Export Clean CSV</a>
            <a href="/api/dataset/export?format=excel" class="btn btn-outline btn-sm"><i data-lucide="file-spreadsheet"></i> Export Excel</a>
            <button class="btn btn-primary btn-sm" onclick="DataMgmtModule.runPipeline()"><i data-lucide="play"></i> Execute Pipeline</button>
          </div>
        </div>

        <div style="display: flex; gap: 2rem; flex-wrap: wrap; background: var(--bg-tertiary); padding: 1rem; border-radius: 8px;">
          <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.84rem; cursor: pointer;">
            <input type="checkbox" id="clean-dedup" checked>
            <span>Deduplicate records (remove identical duplicate rows)</span>
          </label>
          <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.84rem; cursor: pointer;">
            <input type="checkbox" id="clean-impute" checked>
            <span>Impute missing values (median for numeric, 'Unknown' for categories)</span>
          </label>
          <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.84rem; cursor: pointer;">
            <input type="checkbox" id="clean-negatives" checked>
            <span>Filter negative sales & quantities</span>
          </label>
        </div>

        <div id="cleaning-log-box" style="margin-top: 1rem; font-family: var(--font-mono); font-size: 0.78rem; color: #a5b4fc; background: var(--bg-card); padding: 0.75rem; border-radius: 6px; border: 1px solid var(--border-subtle); display: none;"></div>
      </div>

      <!-- Column Schema Inspector & Mapper -->
      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">Column Schema Mapping & Type Inspector</div>
            <div class="card-desc">Review detected fields and map incoming columns to internal analytics features</div>
          </div>
          <button class="btn btn-primary btn-sm" onclick="DataMgmtModule.saveRemap()">Apply Mapping Changes</button>
        </div>
        <div class="table-wrapper">
          <table class="data-table" id="columns-schema-table">
            <thead>
              <tr>
                <th>Dataset Column</th>
                <th>Inferred Type</th>
                <th>Missing Values</th>
                <th>Unique Values</th>
                <th>Sample Values</th>
                <th>Mapped Analytic Feature</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>

      <!-- Paginated Dataset Table Preview -->
      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title">Live Cleaned Dataset Preview</div>
            <div class="card-desc">Search, inspect, and verify tabular rows currently driving the analytics</div>
          </div>
          <div style="display: flex; gap: 0.75rem; align-items: center;">
            <input type="text" id="preview-search" class="filter-group" placeholder="Search rows..." style="background: var(--bg-tertiary); color: #fff; width: 200px;" oninput="DataMgmtModule.handleSearch(this.value)">
            <select id="preview-page-size" class="filter-select filter-group" onchange="DataMgmtModule.handlePageSize(this.value)">
              <option value="15">15 rows</option>
              <option value="30">30 rows</option>
              <option value="50">50 rows</option>
            </select>
          </div>
        </div>

        <div class="table-wrapper" id="preview-table-container">
          <div style="color: var(--text-muted); padding: 1rem;">Loading preview...</div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; font-size: 0.82rem; color: var(--text-muted);">
          <div id="preview-pagination-info">Showing rows</div>
          <div style="display: flex; gap: 0.5rem;">
            <button class="btn btn-outline btn-sm" id="prev-page-btn" onclick="DataMgmtModule.prevPage()">&larr; Previous</button>
            <button class="btn btn-outline btn-sm" id="next-page-btn" onclick="DataMgmtModule.nextPage()">Next &rarr;</button>
          </div>
        </div>
      </div>
    `;

    if (window.lucide) lucide.createIcons();

    // Drag-and-drop listener setup
    const dropzone = document.getElementById('upload-dropzone');
    if (dropzone) {
      ['dragenter', 'dragover'].forEach(evt => {
        dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
      });
      ['dragleave', 'drop'].forEach(evt => {
        dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.remove('dragover'); });
      });
      dropzone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          DataMgmtModule.handleFileUpload(e.dataTransfer.files[0]);
        }
      });
    }

    await this.refresh();
  },

  async refresh() {
    try {
      this.profileData = await API.getDatasetProfile();
      this.renderHealthAudit(this.profileData);
      this.renderSchemaTable(this.profileData);
      await this.fetchPreview();
    } catch (err) {
      console.error('Error refreshing data management view:', err);
    }
  },

  renderHealthAudit(profile) {
    const container = document.getElementById('health-audit-content');
    if (!container || !profile) return;

    const scoreColor = profile.health_score >= 80 ? 'var(--accent-emerald)' : (profile.health_score >= 60 ? 'var(--accent-amber)' : 'var(--accent-rose)');

    container.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; background: var(--bg-tertiary); padding: 1.25rem; border-radius: 8px;">
        <div style="display: flex; align-items: center; gap: 1.25rem;">
          <div class="health-score-circle" style="border-color: ${scoreColor}; color: ${scoreColor};">
            ${profile.health_score}
          </div>
          <div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #fff;">Dataset Integrity Index</div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">Calculated across completeness, schema coverage & duplicates</div>
          </div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 0.8rem; color: var(--text-muted);">Active File</div>
          <div style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary);">${State.datasetStatus.name}</div>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
        <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px;">
          <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Total Rows</div>
          <div style="font-size: 1.2rem; font-weight: 700; color: #fff;">${Format.number(profile.total_rows)}</div>
        </div>
        <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px;">
          <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Total Columns</div>
          <div style="font-size: 1.2rem; font-weight: 700; color: #fff;">${profile.total_columns}</div>
        </div>
        <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px;">
          <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Duplicate Rows</div>
          <div style="font-size: 1.2rem; font-weight: 700; color: ${profile.duplicate_rows > 0 ? 'var(--accent-amber)' : '#fff'};">
            ${Format.number(profile.duplicate_rows)} (${profile.duplicate_percentage}%)
          </div>
        </div>
        <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px;">
          <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Missing Cells</div>
          <div style="font-size: 1.2rem; font-weight: 700; color: ${profile.total_missing_cells > 0 ? 'var(--accent-amber)' : '#fff'};">
            ${Format.number(profile.total_missing_cells)} (${profile.missing_cells_percentage}%)
          </div>
        </div>
      </div>
    `;
  },

  renderSchemaTable(profile) {
    const tbody = document.querySelector('#columns-schema-table tbody');
    if (!tbody || !profile || !profile.columns) return;

    const canonicalOptions = [
      { key: '', label: '-- Not Mapped --' },
      { key: 'order_id', label: 'Order ID (Required)' },
      { key: 'order_date', label: 'Order Date (Required)' },
      { key: 'sales', label: 'Sales / Revenue (Required)' },
      { key: 'customer_id', label: 'Customer ID' },
      { key: 'customer_name', label: 'Customer Name' },
      { key: 'product_id', label: 'Product ID' },
      { key: 'product_name', label: 'Product Name' },
      { key: 'category', label: 'Product Category' },
      { key: 'sub_category', label: 'Sub-Category' },
      { key: 'quantity', label: 'Quantity Sold' },
      { key: 'unit_price', label: 'Unit Price' },
      { key: 'discount', label: 'Discount Rate' },
      { key: 'profit', label: 'Net Profit' },
      { key: 'unit_cost', label: 'Unit Cost' },
      { key: 'region', label: 'Region' },
      { key: 'state', label: 'State' },
      { key: 'city', label: 'City' },
      { key: 'country', label: 'Country' },
      { key: 'payment_method', label: 'Payment Method' },
      { key: 'segment', label: 'Customer Segment' }
    ];

    tbody.innerHTML = profile.columns.map(col => {
      const selectHtml = `
        <select class="filter-select filter-group schema-col-select" data-raw-col="${col.name}">
          ${canonicalOptions.map(opt => `
            <option value="${opt.key}" ${col.mapped_to === opt.key ? 'selected' : ''}>${opt.label}</option>
          `).join('')}
        </select>
      `;

      return `
        <tr>
          <td style="font-weight: 600; color: #fff;">${col.name}</td>
          <td><span class="badge" style="background: rgba(255,255,255,0.06);">${col.type}</span></td>
          <td style="color: ${col.missing_count > 0 ? 'var(--accent-amber)' : 'var(--text-muted)'};">
            ${col.missing_count} (${col.missing_percentage}%)
          </td>
          <td>${col.unique_values}</td>
          <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-secondary);">
            ${col.sample_values ? col.sample_values.join(', ') : 'None'}
          </td>
          <td>${selectHtml}</td>
        </tr>
      `;
    }).join('');
  },

  async fetchPreview() {
    try {
      this.previewData = await API.getDatasetPreview(this.currentPage, this.pageSize, this.searchQuery);
      this.renderPreviewTable(this.previewData);
    } catch (err) {
      console.error('Error fetching preview table:', err);
    }
  },

  renderPreviewTable(data) {
    const container = document.getElementById('preview-table-container');
    const pageInfo = document.getElementById('preview-pagination-info');
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');

    if (!container || !data || !data.columns) return;

    if (data.rows.length === 0) {
      container.innerHTML = `<div style="padding: 1.5rem; text-align: center; color: var(--text-muted);">No records match current search.</div>`;
      return;
    }

    const tableHtml = `
      <table class="data-table">
        <thead>
          <tr>
            ${data.columns.map(c => `<th>${c}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${data.rows.map(row => `
            <tr>
              ${data.columns.map(c => `<td>${row[c] !== null ? row[c] : '<i style="color: var(--text-muted);">null</i>'}</td>`).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;

    container.innerHTML = tableHtml;

    if (pageInfo) {
      const start = (data.page - 1) * data.page_size + 1;
      const end = Math.min(start + data.rows.length - 1, data.total);
      pageInfo.textContent = `Showing ${start}-${end} of ${Format.number(data.total)} records (Page ${data.page} of ${data.total_pages})`;
    }

    if (prevBtn) prevBtn.disabled = data.page <= 1;
    if (nextBtn) nextBtn.disabled = data.page >= data.total_pages;
  },

  handleSearch(val) {
    this.searchQuery = val;
    this.currentPage = 1;
    this.fetchPreview();
  },

  handlePageSize(val) {
    this.pageSize = parseInt(val, 10);
    this.currentPage = 1;
    this.fetchPreview();
  },

  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.fetchPreview();
    }
  },

  nextPage() {
    if (this.previewData && this.currentPage < this.previewData.total_pages) {
      this.currentPage++;
      this.fetchPreview();
    }
  },

  async handleFileUpload(file) {
    if (!file) return;
    App.showToast(`Uploading and analyzing '${file.name}'...`, 'info');
    try {
      const res = await API.uploadDataset(file);
      // Recalibrate state with new dataset schema, date bounds, and categories
      State.setDatasetStatus(res.status);
      App.showToast(`Successfully processed '${file.name}' (${Format.number(res.status.total_rows)} rows)!`, 'success');
      
      // Auto-switch to Executive Dashboard so the user IMMEDIATELY sees their analytics
      setTimeout(() => {
        State.setModule('executive');
        App.showToast(`Analytics dashboard updated for '${file.name}'.`, 'success');
      }, 400);
    } catch (err) {
      App.showToast(`Upload failed: ${err.message}`, 'error');
    }
  },

  async resetSample() {
    App.showToast('Resetting to enterprise sample dataset...');
    try {
      const res = await API.loadSampleDataset();
      State.setDatasetStatus(res.status);
      App.showToast('Reset to enterprise sample dataset.', 'success');
      await this.render(document.getElementById('view-data-mgmt'));
    } catch (err) {
      App.showToast(`Reset failed: ${err.message}`, 'error');
    }
  },

  async runPipeline() {
    const dropDuplicates = document.getElementById('clean-dedup').checked;
    const imputeMissing = document.getElementById('clean-impute').checked;
    const removeNegativeSales = document.getElementById('clean-negatives').checked;

    App.showToast('Executing data preprocessing pipeline...');
    try {
      const res = await API.preprocessDataset({ dropDuplicates, imputeMissing, removeNegativeSales });
      State.setDatasetStatus(res.status);

      const logBox = document.getElementById('cleaning-log-box');
      if (logBox && res.clean_report) {
        logBox.style.display = 'block';
        logBox.innerHTML = `
          <b>Pipeline Transformation Log:</b><br>
          • Rows Retained: ${res.clean_report.final_rows} / ${res.clean_report.original_rows} (${res.clean_report.rows_retained_pct}%)<br>
          ${(res.clean_report.cleaning_log || []).map(l => `• ${l}`).join('<br>')}
        `;
      }
      App.showToast('Preprocessing pipeline completed successfully!', 'success');
      await this.fetchPreview();
    } catch (err) {
      App.showToast(`Pipeline failed: ${err.message}`, 'error');
    }
  },

  async saveRemap() {
    const selects = document.querySelectorAll('.schema-col-select');
    const newMapping = {};

    selects.forEach(sel => {
      const canonicalKey = sel.value;
      const rawCol = sel.getAttribute('data-raw-col');
      if (canonicalKey) {
        newMapping[canonicalKey] = rawCol;
      }
    });

    App.showToast('Recalibrating schema mappings...');
    try {
      const res = await API.remapDataset(newMapping);
      State.setDatasetStatus(res.status);
      App.showToast('Schema mapped and analytics recalibrated!', 'success');
      await this.refresh();
    } catch (err) {
      App.showToast(`Remap error: ${err.message}`, 'error');
    }
  }
};
