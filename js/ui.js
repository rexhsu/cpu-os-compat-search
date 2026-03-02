/**
 * UI Renderer - DOM rendering for autocomplete, CPU info, compatibility results.
 */
const UI = (() => {

  /**
   * Render autocomplete dropdown items.
   */
  function renderAutocomplete(cpus, container, onSelect) {
    container.innerHTML = '';
    if (cpus.length === 0) {
      container.classList.add('d-none');
      return;
    }

    for (const cpu of cpus) {
      const item = document.createElement('div');
      item.className = 'autocomplete-item';
      item.dataset.cpuId = cpu.id;

      const levelClass = `badge-level-${cpu.x86_64_level}`;
      item.innerHTML = `
        <div>
          <span class="cpu-name">${escapeHtml(cpu.name)}</span>
          <div class="cpu-meta">${escapeHtml(cpu.codename || '')} | ${escapeHtml(cpu.segment || '')}</div>
        </div>
        <span class="badge ${levelClass}">v${cpu.x86_64_level}</span>
      `;

      item.addEventListener('click', () => onSelect(cpu));
      container.appendChild(item);
    }

    container.classList.remove('d-none');
  }

  /**
   * Render CPU information card.
   */
  function renderCpuInfo(cpu) {
    const nameEl = document.getElementById('cpu-name');
    const badgeEl = document.getElementById('cpu-level-badge');
    const specsEl = document.getElementById('cpu-specs');
    const featuresEl = document.getElementById('cpu-features');

    nameEl.textContent = cpu.name;
    badgeEl.textContent = `x86-64-v${cpu.x86_64_level}`;
    badgeEl.className = `badge badge-level-${cpu.x86_64_level}`;

    // Specs grid
    const specs = [
      { label: 'Cores', value: cpu.cores || '-' },
      { label: 'Threads', value: cpu.threads || '-' },
      { label: 'Base', value: cpu.baseClock ? `${cpu.baseClock} GHz` : '-' },
      { label: 'Boost', value: cpu.boostClock ? `${cpu.boostClock} GHz` : '-' },
      { label: 'TDP', value: cpu.tdpW ? `${cpu.tdpW} W` : '-' },
      { label: 'Socket', value: cpu.socket || '-' },
    ];

    specsEl.innerHTML = specs.map(s => `
      <div class="col-4 col-sm-2 cpu-spec-item">
        <div class="spec-label">${s.label}</div>
        <div class="spec-value">${escapeHtml(String(s.value))}</div>
      </div>
    `).join('');

    // Feature badges
    const featureLabels = {
      sse42: 'SSE4.2', popcnt: 'POPCNT', avx: 'AVX', avx2: 'AVX2',
      avx512: 'AVX-512', fma: 'FMA', bmi1: 'BMI1', bmi2: 'BMI2',
      aes_ni: 'AES-NI', tpm2: 'TPM 2.0',
    };

    featuresEl.innerHTML = Object.entries(featureLabels).map(([key, label]) => {
      const has = cpu.features[key];
      const cls = has ? 'supported' : 'not-supported';
      const icon = has ? 'bi-check-circle-fill' : 'bi-x-circle';
      return `<span class="badge feature-badge ${cls}"><i class="bi ${icon}"></i> ${label}</span>`;
    }).join(' ');

    document.getElementById('cpu-info').classList.remove('d-none');
  }

  /**
   * Render OS compatibility results for a CPU.
   */
  function renderCpuCompatResults(results) {
    const container = document.getElementById('cpu-compat-results');
    container.innerHTML = '';

    for (const result of results) {
      const card = document.createElement('div');
      card.className = `card compat-card compat-${result.status} mb-2`;

      const statusIcon = result.status === 'pass' ? 'bi-check-circle-fill' :
                          result.status === 'fail' ? 'bi-x-circle-fill' : 'bi-exclamation-triangle-fill';
      const statusText = result.status === 'pass' ? 'Compatible' :
                          result.status === 'fail' ? 'Not Compatible' : 'Partial';
      const statusClass = `text-${result.status}`;

      card.innerHTML = `
        <div class="card-body py-2 px-3">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>${escapeHtml(result.os.name)}</strong>
              <span class="text-muted ms-2 small">(v${result.os.x86_64_level} / ${result.os.minRamGB} GB RAM)</span>
            </div>
            <span class="compat-status ${statusClass}">
              <i class="bi ${statusIcon}"></i> ${statusText}
            </span>
          </div>
          <div class="compat-reason">${result.reasons.map(escapeHtml).join(' | ')}</div>
        </div>
      `;

      container.appendChild(card);
    }
  }

  /**
   * Render OS autocomplete dropdown items.
   */
  function renderOsAutocomplete(osList, container, onSelect) {
    container.innerHTML = '';
    if (osList.length === 0) {
      container.classList.add('d-none');
      return;
    }

    for (const os of osList) {
      const item = document.createElement('div');
      item.className = 'autocomplete-item';
      item.dataset.osId = os.id;

      const levelClass = `badge-level-${os.x86_64_level}`;
      item.innerHTML = `
        <div>
          <span class="cpu-name">${escapeHtml(os.name)}</span>
          <div class="cpu-meta">${escapeHtml(os.vendor || '')} | ${escapeHtml(os.type || '')}</div>
        </div>
        <span class="badge ${levelClass}">v${os.x86_64_level}</span>
      `;

      item.addEventListener('click', () => onSelect(os));
      container.appendChild(item);
    }

    container.classList.remove('d-none');
  }

  /**
   * Render OS details card.
   */
  function renderOsInfo(os) {
    const nameEl = document.getElementById('os-name');
    const detailsEl = document.getElementById('os-details');

    nameEl.textContent = os.name;

    const reqs = os.additionalRequirements || {};
    const additionalItems = [];
    if (reqs.tpm2) additionalItems.push('TPM 2.0');
    if (reqs.uefi) additionalItems.push('UEFI');
    if (reqs.secureBootCapable) additionalItems.push('Secure Boot');
    if (reqs.slat) additionalItems.push('SLAT');
    if (reqs.cpuWhitelist) additionalItems.push('CPU Whitelist');

    detailsEl.innerHTML = `
      <table class="table table-sm os-detail-table mb-0">
        <tr><td class="label-col">x86-64 Level</td><td><span class="badge badge-level-${os.x86_64_level}">v${os.x86_64_level}</span></td></tr>
        <tr><td class="label-col">Min RAM</td><td>${os.minRamGB} GB${os.minRamGBDesktop ? ` (Core) / ${os.minRamGBDesktop} GB (Desktop)` : ''}${os.minRamGBServer ? ` (Desktop) / ${os.minRamGBServer} GB (Server)` : ''}</td></tr>
        <tr><td class="label-col">Min Storage</td><td>${os.minStorageGB} GB</td></tr>
        <tr><td class="label-col">Required Features</td><td>${os.requiredFeatures?.length ? os.requiredFeatures.join(', ').toUpperCase() : 'None (basic x86-64)'}</td></tr>
        ${additionalItems.length ? `<tr><td class="label-col">Additional</td><td>${additionalItems.join(', ')}</td></tr>` : ''}
        <tr><td class="label-col">Release</td><td>${os.releaseDate || '-'}</td></tr>
        <tr><td class="label-col">EOL</td><td>${os.eol || '-'}</td></tr>
        ${os.notes ? `<tr><td class="label-col">Notes</td><td class="text-muted small">${escapeHtml(os.notes)}</td></tr>` : ''}
      </table>
    `;

    document.getElementById('os-info').classList.remove('d-none');
  }

  /**
   * Render compatible CPU list for an OS.
   */
  function renderOsCompatResults(results, filterText = '') {
    const container = document.getElementById('os-compat-results');
    const countEl = document.getElementById('os-cpu-count');
    container.innerHTML = '';

    let filtered = results;
    if (filterText) {
      const q = filterText.toLowerCase();
      filtered = results.filter(r =>
        r.cpu.name.toLowerCase().includes(q) ||
        (r.cpu.processorNumber || '').toLowerCase().includes(q)
      );
    }

    // Show only compatible (pass/warn)
    const compatible = filtered.filter(r => r.status !== 'fail');
    const incompatible = filtered.filter(r => r.status === 'fail');

    countEl.textContent = `${compatible.length} compatible / ${incompatible.length} incompatible (of ${results.length} total)`;

    // Render max 100 to avoid DOM overload
    const toShow = compatible.slice(0, 100);
    if (toShow.length === 0) {
      container.innerHTML = '<p class="text-muted">No compatible CPUs found for this filter.</p>';
      return;
    }

    const list = document.createElement('div');
    list.className = 'card';
    const listBody = document.createElement('div');
    listBody.className = 'card-body p-0';

    for (const result of toShow) {
      const item = document.createElement('div');
      item.className = 'cpu-list-item';
      const levelClass = `badge-level-${result.cpu.x86_64_level}`;
      const statusIcon = result.status === 'pass' ? 'text-success' : 'text-warning';
      item.innerHTML = `
        <div>
          <i class="bi bi-check-circle-fill ${statusIcon}"></i>
          <span class="ms-1">${escapeHtml(result.cpu.name)}</span>
          ${result.status === 'warn' ? `<span class="text-muted small ms-1">(${result.reasons.join(', ')})</span>` : ''}
        </div>
        <span class="badge ${levelClass}">v${result.cpu.x86_64_level}</span>
      `;
      listBody.appendChild(item);
    }

    list.appendChild(listBody);
    container.appendChild(list);

    if (compatible.length > 100) {
      container.insertAdjacentHTML('beforeend',
        `<p class="text-muted small mt-2">Showing first 100 of ${compatible.length} compatible CPUs. Use the filter to narrow results.</p>`
      );
    }
  }

  /**
   * Show data metadata in footer.
   */
  function showMetadata(meta) {
    const dateEl = document.getElementById('data-date');
    const countsEl = document.getElementById('data-counts');

    dateEl.textContent = meta.intelGenerated ?
      new Date(meta.intelGenerated).toLocaleDateString() : 'Unknown';
    countsEl.textContent = `${meta.intelCount} Intel + ${meta.amdCount} AMD CPUs | ${meta.osCount} Operating Systems`;
    document.getElementById('data-meta').classList.remove('d-none');
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }


  /**
   * Render detailed CPU + OS compatibility report.
   */
  function renderCpuOsReport(cpu, os, result) {
    const container = document.getElementById('cpuos-result');

    const verdictIcon = result.overall === 'pass' ? 'bi-check-circle-fill' :
                        result.overall === 'fail' ? 'bi-x-circle-fill' : 'bi-exclamation-triangle-fill';
    const verdictText = result.overall === 'pass' ? 'Compatible' :
                        result.overall === 'fail' ? 'Not Compatible' : 'Partial Compatibility';
    const verdictClass = `verdict-${result.overall}`;

    const checksHtml = result.checks.map(c => {
      const icon = c.status === 'pass' ? 'bi-check-circle-fill text-success' :
                   c.status === 'fail' ? 'bi-x-circle-fill text-danger' :
                   c.status === 'warn' ? 'bi-exclamation-triangle-fill text-warning' :
                   'bi-dash-circle text-muted';
      return `
        <tr class="detail-check-row">
          <td><i class="bi ${icon}"></i></td>
          <td class="fw-semibold">${escapeHtml(c.name)}</td>
          <td class="text-muted">${escapeHtml(c.detail)}</td>
        </tr>`;
    }).join('');

    container.innerHTML = `
      <!-- CPU summary -->
      <div class="card mb-3">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h6 class="mb-0"><i class="bi bi-cpu"></i> ${escapeHtml(cpu.name)}</h6>
          <span class="badge badge-level-${cpu.x86_64_level}">v${cpu.x86_64_level}</span>
        </div>
        <div class="card-body py-2 small text-muted">
          ${cpu.cores ? cpu.cores + ' cores' : ''}${cpu.boostClock ? ' / ' + cpu.boostClock + ' GHz boost' : ''}${cpu.socket ? ' / ' + escapeHtml(cpu.socket) : ''}
        </div>
      </div>

      <!-- OS summary -->
      <div class="card mb-3">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h6 class="mb-0"><i class="bi bi-windows"></i> ${escapeHtml(os.name)}</h6>
          <span class="badge badge-level-${os.x86_64_level}">v${os.x86_64_level}</span>
        </div>
        <div class="card-body py-2 small text-muted">
          Min RAM: ${os.minRamGB} GB | Min Storage: ${os.minStorageGB} GB
        </div>
      </div>

      <!-- Verdict -->
      <div class="verdict-box ${verdictClass} mb-3">
        <i class="bi ${verdictIcon}"></i>
        <span>${verdictText}</span>
      </div>

      <!-- Detailed checks table -->
      <div class="card">
        <div class="card-header"><h6 class="mb-0">Detailed Checks</h6></div>
        <div class="card-body p-0">
          <table class="table table-sm mb-0">
            <tbody>
              ${checksHtml}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  return {
    renderAutocomplete,
    renderOsAutocomplete,
    renderCpuInfo,
    renderCpuCompatResults,
    renderOsInfo,
    renderOsCompatResults,
    renderCpuOsReport,
    showMetadata,
  };
})();
