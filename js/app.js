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

      // Populate OS dropdown
      UI.populateOsSelect(osRequirements);
      UI.showMetadata(metadata);

      // Bind events
      bindCpuSearch();
      bindOsSelect();

    } catch (err) {
      loadingEl.classList.add('d-none');
      errorMsgEl.textContent = `Failed to load data: ${err.message}`;
      errorEl.classList.remove('d-none');
      console.error('Data load error:', err);
    }
  });

  function bindCpuSearch() {
    const input = document.getElementById('cpu-search');
    const dropdown = document.getElementById('cpu-autocomplete');
    let debounceTimer = null;
    let activeIndex = -1;

    function onSelect(cpu) {
      input.value = cpu.name;
      dropdown.classList.add('d-none');
      activeIndex = -1;

      UI.renderCpuInfo(cpu);
      const results = SearchEngine.findCompatibleOs(cpu.id);
      UI.renderCpuCompatResults(results);
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
        UI.renderAutocomplete(results, dropdown, onSelect);
      }, 200);
    });

    // Keyboard navigation
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

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('d-none');
        activeIndex = -1;
      }
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
