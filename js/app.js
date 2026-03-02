/**
 * App - initialization and event binding.
 */
(function () {
  'use strict';

  let currentOsResults = null;
  let cpuOsNav = null;

  document.addEventListener('DOMContentLoaded', async () => {
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('load-error');
    const errorMsgEl = document.getElementById('load-error-msg');
    const mainContent = document.getElementById('main-content');

    try {
      const { osRequirements, metadata } = await DataLoader.loadAll();

      loadingEl.classList.add('d-none');
      mainContent.classList.remove('d-none');

      UI.showMetadata(metadata);

      // Bind events — each in its own try/catch so one failure doesn't break others
      try { bindCpuSearch(); } catch (e) { console.error('bindCpuSearch failed:', e); }
      try { bindOsSelect(); } catch (e) { console.error('bindOsSelect failed:', e); }
      try { bindCpuOsSearch(); } catch (e) { console.error('bindCpuOsSearch failed:', e); }

    } catch (err) {
      loadingEl.classList.add('d-none');
      errorMsgEl.textContent = `Failed to load data: ${err.message}`;
      errorEl.classList.remove('d-none');
      console.error('Data load error:', err);
    }
  });

  /**
   * Shared helper: set up autocomplete on an input + dropdown pair.
   * @param {string} inputId - ID of the text input element
   * @param {string} dropdownId - ID of the dropdown container
   * @param {function} searchFn - function(query) that returns results array
   * @param {function} renderFn - function(results, dropdown, handleSelect) to render items
   * @param {function} onSelect - callback when user selects an item
   * @param {function} getDisplayName - function(item) returning display string for input
   */
  function setupAutocomplete(inputId, dropdownId, { searchFn, renderFn, onSelect, getDisplayName }) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) {
      console.error('setupAutocomplete: element not found', inputId, dropdownId);
      return null;
    }

    let debounceTimer = null;
    let activeIndex = -1;

    function handleSelect(item) {
      input.value = getDisplayName(item);
      dropdown.classList.add('d-none');
      activeIndex = -1;
      onSelect(item);
    }

    input.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const query = input.value.trim();
        if (query.length < 2) {
          dropdown.classList.add('d-none');
          return;
        }
        const results = searchFn(query);
        activeIndex = -1;
        renderFn(results, dropdown, handleSelect);
      }, 200);
    });

    input.addEventListener('keydown', (e) => {
      const items = dropdown.querySelectorAll('.autocomplete-item');
      if (items.length === 0) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIndex = Math.min(activeIndex + 1, items.length - 1);
        updateActiveItem(items);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIndex = Math.max(activeIndex - 1, 0);
        updateActiveItem(items);
      } else if (e.key === 'Enter' && activeIndex >= 0) {
        e.preventDefault();
        items[activeIndex].click();
      } else if (e.key === 'Escape') {
        dropdown.classList.add('d-none');
        activeIndex = -1;
      }
    });

    function updateActiveItem(items) {
      items.forEach((item, i) => {
        item.classList.toggle('active', i === activeIndex);
      });
      if (activeIndex >= 0 && items[activeIndex]) {
        items[activeIndex].scrollIntoView({ block: 'nearest' });
      }
    }

    // Close dropdown on outside mousedown
    document.addEventListener('mousedown', (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('d-none');
        activeIndex = -1;
      }
    });

    return { input, dropdown };
  }

  function setupCpuAutocomplete(inputId, dropdownId, onSelect) {
    return setupAutocomplete(inputId, dropdownId, {
      searchFn: (q) => SearchEngine.searchCpus(q),
      renderFn: UI.renderAutocomplete,
      onSelect,
      getDisplayName: (cpu) => cpu.name,
    });
  }

  function setupOsAutocomplete(inputId, dropdownId, onSelect) {
    return setupAutocomplete(inputId, dropdownId, {
      searchFn: (q) => SearchEngine.searchOs(q),
      renderFn: UI.renderOsAutocomplete,
      onSelect,
      getDisplayName: (os) => os.name,
    });
  }

  function bindCpuSearch() {
    let currentCpu = null;
    setupCpuAutocomplete('cpu-search', 'cpu-autocomplete', (cpu) => {
      currentCpu = cpu;
      UI.renderCpuInfo(cpu);
      const results = SearchEngine.findCompatibleOs(cpu.id);
      UI.renderCpuCompatResults(results, (os) => {
        if (cpuOsNav) cpuOsNav.navigate(currentCpu, os);
      });
    });
  }

  function bindCpuOsSearch() {
    let selectedCpu = null;
    let selectedOs = null;

    function tryRender() {
      if (!selectedCpu || !selectedOs) return;
      const result = SearchEngine.detailedCheck(selectedCpu, selectedOs);
      UI.renderCpuOsReport(selectedCpu, selectedOs, result);
    }

    const cpuAc = setupCpuAutocomplete('cpuos-cpu-search', 'cpuos-cpu-autocomplete', (cpu) => {
      selectedCpu = cpu;
      tryRender();
    });

    const osAc = setupOsAutocomplete('cpuos-os-search', 'cpuos-os-autocomplete', (os) => {
      selectedOs = os;
      tryRender();
    });

    if (!cpuAc || !osAc) return;

    // When user types new CPU text, clear previous selection
    cpuAc.input.addEventListener('input', () => {
      selectedCpu = null;
      const resultEl = document.getElementById('cpuos-result');
      if (resultEl) resultEl.innerHTML = '';
    });

    // When user types new OS text, clear previous selection
    osAc.input.addEventListener('input', () => {
      selectedOs = null;
      const resultEl = document.getElementById('cpuos-result');
      if (resultEl) resultEl.innerHTML = '';
    });

    // Expose navigation for cross-tab linking
    cpuOsNav = {
      navigate(cpu, os) {
        selectedCpu = cpu;
        selectedOs = os;
        cpuAc.input.value = cpu.name;
        osAc.input.value = os.name;
        new bootstrap.Tab(document.getElementById('cpuos-tab')).show();
        tryRender();
      }
    };
  }

  function bindOsSelect() {
    let currentOs = null;
    const filterInput = document.getElementById('os-cpu-filter');

    function cpuClickHandler(cpu) {
      if (cpuOsNav && currentOs) cpuOsNav.navigate(cpu, currentOs);
    }

    setupOsAutocomplete('os-search', 'os-autocomplete', (os) => {
      currentOs = os;
      UI.renderOsInfo(os);
      currentOsResults = SearchEngine.findCompatibleCpus(os.id);
      filterInput.value = '';
      UI.renderOsCompatResults(currentOsResults, '', cpuClickHandler);
    });

    let filterTimer = null;
    filterInput.addEventListener('input', () => {
      clearTimeout(filterTimer);
      filterTimer = setTimeout(() => {
        if (currentOsResults) {
          UI.renderOsCompatResults(currentOsResults, filterInput.value.trim(), cpuClickHandler);
        }
      }, 200);
    });
  }

})();
