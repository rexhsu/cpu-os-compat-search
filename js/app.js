/**
 * App - initialization and event binding.
 */
(function () {
  'use strict';

  let currentOsResults = null;

  document.addEventListener('DOMContentLoaded', async () => {
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('load-error');
    const errorMsgEl = document.getElementById('load-error-msg');
    const mainContent = document.getElementById('main-content');

    try {
      const { osRequirements, metadata } = await DataLoader.loadAll();

      loadingEl.classList.add('d-none');
      mainContent.classList.remove('d-none');

      // Populate OS dropdowns
      UI.populateOsSelect(osRequirements);
      UI.populateCpuOsOsSelect(osRequirements);
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
   * Returns { getSelected, setOnChange } for the caller to hook into.
   */
  function setupAutocomplete(inputId, dropdownId, onSelect) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) {
      console.error('setupAutocomplete: element not found', inputId, dropdownId);
      return null;
    }

    let debounceTimer = null;
    let activeIndex = -1;

    function handleSelect(cpu) {
      input.value = cpu.name;
      dropdown.classList.add('d-none');
      activeIndex = -1;
      onSelect(cpu);
    }

    input.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const query = input.value.trim();
        if (query.length < 2) {
          dropdown.classList.add('d-none');
          return;
        }
        const results = SearchEngine.searchCpus(query);
        activeIndex = -1;
        UI.renderAutocomplete(results, dropdown, handleSelect);
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

    // Close dropdown on outside mousedown (fires before native <select> opens)
    document.addEventListener('mousedown', (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('d-none');
        activeIndex = -1;
      }
    });

    return { input, dropdown };
  }

  function bindCpuSearch() {
    setupAutocomplete('cpu-search', 'cpu-autocomplete', (cpu) => {
      UI.renderCpuInfo(cpu);
      const results = SearchEngine.findCompatibleOs(cpu.id);
      UI.renderCpuCompatResults(results);
    });
  }

  function bindCpuOsSearch() {
    const osSelect = document.getElementById('cpuos-os-select');
    if (!osSelect) {
      console.error('bindCpuOsSearch: cpuos-os-select not found');
      return;
    }

    let selectedCpuOs = null;

    function tryRender() {
      const osId = osSelect.value;
      if (!selectedCpuOs || !osId) return;
      const os = DataLoader.getOsRequirements().find(o => o.id === osId);
      if (!os) return;
      const result = SearchEngine.detailedCheck(selectedCpuOs, os);
      UI.renderCpuOsReport(selectedCpuOs, os, result);
    }

    const ac = setupAutocomplete('cpuos-cpu-search', 'cpuos-cpu-autocomplete', (cpu) => {
      selectedCpuOs = cpu;
      tryRender();
    });

    if (!ac) return;

    // When user types new text, clear previous selection
    ac.input.addEventListener('input', () => {
      selectedCpuOs = null;
      const resultEl = document.getElementById('cpuos-result');
      if (resultEl) resultEl.innerHTML = '';
    });

    osSelect.addEventListener('change', () => {
      tryRender();
    });
  }

  function bindOsSelect() {
    const select = document.getElementById('os-select');
    const filterInput = document.getElementById('os-cpu-filter');

    select.addEventListener('change', () => {
      const osId = select.value;
      if (!osId) {
        document.getElementById('os-info').classList.add('d-none');
        currentOsResults = null;
        return;
      }

      const os = DataLoader.getOsRequirements().find(o => o.id === osId);
      if (!os) return;

      UI.renderOsInfo(os);
      currentOsResults = SearchEngine.findCompatibleCpus(osId);
      filterInput.value = '';
      UI.renderOsCompatResults(currentOsResults);
    });

    let filterTimer = null;
    filterInput.addEventListener('input', () => {
      clearTimeout(filterTimer);
      filterTimer = setTimeout(() => {
        if (currentOsResults) {
          UI.renderOsCompatResults(currentOsResults, filterInput.value.trim());
        }
      }, 200);
    });
  }

})();
