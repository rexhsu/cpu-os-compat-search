/**
 * Data Loader - fetches and indexes CPU/OS JSON data.
 */
const DataLoader = (() => {
  let intelCpus = [];
  let amdCpus = [];
  let allCpus = [];
  let osRequirements = [];
  let cpuWhitelists = new Map(); // dataFile -> { intel: [], amd: [], qualcomm: [] }
  let cpuIndex = new Map(); // id -> cpu
  let metadata = {};

  async function fetchJSON(path) {
    const resp = await fetch(path);
    if (!resp.ok) throw new Error(`Failed to load ${path}: ${resp.status}`);
    return resp.json();
  }

  async function loadAll() {
    const [intelData, amdData, osData] = await Promise.all([
      fetchJSON('data/cpu-intel.json'),
      fetchJSON('data/cpu-amd.json'),
      fetchJSON('data/os-requirements.json'),
    ]);

    intelCpus = intelData.cpus || [];
    amdCpus = amdData.cpus || [];
    allCpus = [...intelCpus, ...amdCpus];
    osRequirements = osData.operatingSystems || [];

    // Discover and load all CPU whitelist files referenced by OS entries
    const whitelistFiles = new Set();
    for (const os of osRequirements) {
      const wl = os.additionalRequirements?.cpuWhitelist;
      if (wl?.dataFile) whitelistFiles.add(wl.dataFile);
    }

    const whitelistPromises = [...whitelistFiles].map(async (filename) => {
      try {
        const data = await fetchJSON(`data/${filename}`);
        cpuWhitelists.set(filename, {
          intel: data.intel || [],
          amd: data.amd || [],
          qualcomm: data.qualcomm || [],
          metadata: data.metadata || {},
        });
      } catch (err) {
        console.warn(`Failed to load whitelist ${filename}:`, err);
      }
    });
    await Promise.all(whitelistPromises);

    // Build index
    cpuIndex.clear();
    for (const cpu of allCpus) {
      cpuIndex.set(cpu.id, cpu);
    }

    metadata = {
      intelCount: intelCpus.length,
      amdCount: amdCpus.length,
      osCount: osRequirements.length,
      intelGenerated: intelData.metadata?.generated,
      amdGenerated: amdData.metadata?.generated,
    };

    return { allCpus, osRequirements, cpuWhitelists, metadata };
  }

  function getCpuById(id) {
    return cpuIndex.get(id) || null;
  }

  function getAllCpus() {
    return allCpus;
  }

  function getOsRequirements() {
    return osRequirements;
  }

  function getCpuWhitelist(dataFile) {
    return cpuWhitelists.get(dataFile) || { intel: [], amd: [], qualcomm: [] };
  }

  function getMetadata() {
    return metadata;
  }

  return { loadAll, getCpuById, getAllCpus, getOsRequirements, getCpuWhitelist, getMetadata };
})();
