/**
 * Search Engine - CPU/OS compatibility checking logic.
 */
const SearchEngine = (() => {

  /**
   * Check if a CPU is on the Windows 11 supported list.
   */
  function isOnWin11Whitelist(cpu) {
    const whitelist = DataLoader.getWin11Whitelist();
    const entries = cpu.vendor === 'intel' ? whitelist.intel : whitelist.amd;
    const cpuName = cpu.name.toLowerCase();
    const cpuProc = (cpu.processorNumber || '').toLowerCase();

    for (const entry of entries) {
      const entryLower = entry.toLowerCase();
      if (cpuName.includes(entryLower) || entryLower.includes(cpuProc)) {
        return true;
      }
      // Partial match: processor number in whitelist entry
      if (cpuProc && entryLower.includes(cpuProc)) {
        return true;
      }
      // Match by processor number pattern
      if (cpuProc && cpuProc.length > 3) {
        const procClean = cpuProc.replace(/[^a-z0-9]/g, '');
        const entryClean = entryLower.replace(/[^a-z0-9]/g, '');
        if (entryClean.includes(procClean) || procClean.includes(entryClean)) {
          return true;
        }
      }
    }
    return false;
  }

  /**
   * Check compatibility between a CPU and an OS.
   * Returns { compatible: bool, status: 'pass'|'fail'|'warn', reasons: string[] }
   */
  function checkCompatibility(cpu, os) {
    const reasons = [];
    let status = 'pass';

    // Check x86-64 level
    if (cpu.x86_64_level < os.x86_64_level) {
      status = 'fail';
      reasons.push(`Requires x86-64-v${os.x86_64_level}, CPU is v${cpu.x86_64_level}`);
    }

    // Check required features
    if (os.requiredFeatures && os.requiredFeatures.length > 0) {
      const missing = os.requiredFeatures.filter(f => !cpu.features[f]);
      if (missing.length > 0) {
        status = 'fail';
        reasons.push(`Missing features: ${missing.join(', ')}`);
      }
    }

    // Check TPM 2.0 requirement
    if (os.additionalRequirements?.tpm2 && !cpu.features.tpm2) {
      if (status !== 'fail') status = 'warn';
      reasons.push('TPM 2.0 required (may need discrete TPM module)');
    }

    // Check Windows 11 CPU whitelist
    if (os.additionalRequirements?.win11CpuWhitelist) {
      if (!isOnWin11Whitelist(cpu)) {
        // Whitelist check: use generation as heuristic fallback
        const isLikelySupported = (
          (cpu.vendor === 'intel' && cpu.generation >= 8) ||
          (cpu.vendor === 'amd' && cpu.x86_64_level >= 3)
        );
        if (!isLikelySupported) {
          status = 'fail';
          reasons.push('Not on Windows 11 supported CPU list');
        } else {
          if (status === 'pass') status = 'warn';
          reasons.push('Not found in whitelist (likely supported based on generation)');
        }
      }
    }

    if (reasons.length === 0) {
      reasons.push('All requirements met');
    }

    return {
      compatible: status !== 'fail',
      status,
      reasons,
    };
  }

  /**
   * Find all OS compatibility results for a given CPU.
   */
  function findCompatibleOs(cpuId) {
    const cpu = DataLoader.getCpuById(cpuId);
    if (!cpu) return [];

    const osList = DataLoader.getOsRequirements();
    return osList.map(os => ({
      os,
      ...checkCompatibility(cpu, os),
    }));
  }

  /**
   * Find all CPUs compatible with a given OS.
   */
  function findCompatibleCpus(osId) {
    const osList = DataLoader.getOsRequirements();
    const os = osList.find(o => o.id === osId);
    if (!os) return [];

    const allCpus = DataLoader.getAllCpus();
    return allCpus
      .map(cpu => ({
        cpu,
        ...checkCompatibility(cpu, os),
      }))
      .sort((a, b) => {
        // Sort: pass first, then warn, then fail; within same status sort by name
        const statusOrder = { pass: 0, warn: 1, fail: 2 };
        const diff = statusOrder[a.status] - statusOrder[b.status];
        if (diff !== 0) return diff;
        return a.cpu.name.localeCompare(b.cpu.name);
      });
  }

  /**
   * Fuzzy search CPUs by query string.
   */
  function searchCpus(query, limit = 20) {
    if (!query || query.length < 2) return [];

    const allCpus = DataLoader.getAllCpus();
    const q = query.toLowerCase().replace(/\s+/g, ' ').trim();
    const terms = q.split(' ');

    const scored = [];
    for (const cpu of allCpus) {
      const nameL = cpu.name.toLowerCase();
      const procL = (cpu.processorNumber || '').toLowerCase();
      const codenameL = (cpu.codename || '').toLowerCase();

      let score = 0;

      // Exact processor number match
      if (procL === q) {
        score += 100;
      } else if (procL.includes(q)) {
        score += 50;
      }

      // Full name match
      if (nameL.includes(q)) {
        score += 40;
      }

      // Term-by-term matching
      let allTermsMatch = true;
      for (const term of terms) {
        if (nameL.includes(term) || procL.includes(term) || codenameL.includes(term)) {
          score += 10;
        } else {
          allTermsMatch = false;
        }
      }
      if (allTermsMatch && terms.length > 1) {
        score += 20;
      }

      if (score > 0) {
        scored.push({ cpu, score });
      }
    }

    scored.sort((a, b) => b.score - a.score || a.cpu.name.localeCompare(b.cpu.name));
    return scored.slice(0, limit).map(s => s.cpu);
  }

  /**
   * Detailed one-to-one compatibility check between a CPU and an OS.
   * Returns { overall: 'pass'|'warn'|'fail', checks: [{name, status, detail}] }
   */
  function detailedCheck(cpu, os) {
    const checks = [];
    let overall = 'pass';

    // x86-64 Level check
    if (cpu.x86_64_level >= os.x86_64_level) {
      checks.push({
        name: 'x86-64 Level',
        status: 'pass',
        detail: `CPU v${cpu.x86_64_level} meets required v${os.x86_64_level}`,
      });
    } else {
      overall = 'fail';
      checks.push({
        name: 'x86-64 Level',
        status: 'fail',
        detail: `CPU v${cpu.x86_64_level} does not meet required v${os.x86_64_level}`,
      });
    }

    // Per-feature checks
    const featuresToCheck = ['sse42', 'popcnt', 'avx', 'avx2', 'fma', 'bmi1', 'bmi2'];
    const featureLabels = {
      sse42: 'SSE4.2', popcnt: 'POPCNT', avx: 'AVX', avx2: 'AVX2',
      fma: 'FMA', bmi1: 'BMI1', bmi2: 'BMI2',
    };

    for (const feat of featuresToCheck) {
      const required = os.requiredFeatures && os.requiredFeatures.includes(feat);
      const has = !!cpu.features[feat];

      if (!required) {
        checks.push({
          name: featureLabels[feat],
          status: has ? 'pass' : 'info',
          detail: required ? '' : (has ? 'Supported (not required by OS)' : 'Not supported (not required by OS)'),
        });
      } else if (has) {
        checks.push({
          name: featureLabels[feat],
          status: 'pass',
          detail: 'Required and supported',
        });
      } else {
        overall = 'fail';
        checks.push({
          name: featureLabels[feat],
          status: 'fail',
          detail: 'Required but not supported',
        });
      }
    }

    // TPM 2.0 check
    if (os.additionalRequirements?.tpm2) {
      if (cpu.features.tpm2) {
        checks.push({ name: 'TPM 2.0', status: 'pass', detail: 'Required and supported' });
      } else {
        if (overall !== 'fail') overall = 'warn';
        checks.push({ name: 'TPM 2.0', status: 'warn', detail: 'Required (may need discrete TPM module)' });
      }
    }

    // Win11 CPU Whitelist check
    if (os.additionalRequirements?.win11CpuWhitelist) {
      if (isOnWin11Whitelist(cpu)) {
        checks.push({ name: 'Win11 CPU Whitelist', status: 'pass', detail: 'CPU is on supported list' });
      } else {
        const isLikelySupported = (
          (cpu.vendor === 'intel' && cpu.generation >= 8) ||
          (cpu.vendor === 'amd' && cpu.x86_64_level >= 3)
        );
        if (!isLikelySupported) {
          overall = 'fail';
          checks.push({ name: 'Win11 CPU Whitelist', status: 'fail', detail: 'Not on Windows 11 supported CPU list' });
        } else {
          if (overall === 'pass') overall = 'warn';
          checks.push({ name: 'Win11 CPU Whitelist', status: 'warn', detail: 'Not found in whitelist (likely supported based on generation)' });
        }
      }
    }

    return { overall, checks };
  }

  return { checkCompatibility, findCompatibleOs, findCompatibleCpus, searchCpus, isOnWin11Whitelist, detailedCheck };
})();
