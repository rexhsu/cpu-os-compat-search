/**
 * Data Loader - fetches and indexes CPU/OS JSON data.
 */
const DataLoader = (() => {
  let intelCpus = [];
  let amdCpus = [];
  let allCpus = [];
  let osRequirements = [];
  let win11Whitelist = { intel: [], amd: [], qualcomm: [] };
  let cpuIndex = new Map(); // id -> cpu
  let metadata = {};

  async function fetchJSON(path) {
    const resp = await fetch(path);
    if (!resp.ok) throw new Error(`Failed to load ${path}: ${resp.status}`);
    return resp.json();
  }

  async function loadAll() {
    const [intelData, amdData, osData, win11Data] = await Promise.all([
      fetchJSON('data/cpu-intel.json'),
      fetchJSON('data/cpu-amd.json'),
      fetchJSON('data/os-requirements.json'),
      fetchJSON('data/windows11-supported-cpus.json'),
    ]);

    intelCpus = intelData.cpus || [];
    amdCpus = amdData.cpus || [];
    allCpus = [...intelCpus, ...amdCpus];
    osRequirements = osData.operatingSystems || [];
    win11Whitelist = {
      intel: win11Data.intel || [],
      amd: win11Data.amd || [],
      qualcomm: win11Data.qualcomm || [],
    };

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

    return { allCpus, osRequirements, win11Whitelist, metadata };
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

  function getWin11Whitelist() {
    return win11Whitelist;
  }

  function getMetadata() {
    return metadata;
  }

  return { loadAll, getCpuById, getAllCpus, getOsRequirements, getWin11Whitelist, getMetadata };
})();
