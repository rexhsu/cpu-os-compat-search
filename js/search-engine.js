/**
 * Search Engine - CPU/OS compatibility checking logic.
 */
const SearchEngine = (() => {

  /**
   * Check if a CPU is on a Windows supported CPU list.
   */
  function isOnCpuWhitelist(cpu, dataFile) {
    const whitelist = DataLoader.getCpuWhitelist(dataFile);
    if (cpu.vendor === 'intel') return matchesIntelWhitelist(cpu, whitelist.intel);
    if (cpu.vendor === 'amd') return matchesAmdWhitelist(cpu, whitelist.amd);
    return false;
  }

  /**
   * Extract series prefix from a series number like "G4000", "W-1200", "4000U".
   * Strips trailing letter suffix then trailing zeros: "G4000"→"g4", "W-1200"→"w-12", "4000U"→"4"
   */
  function getSeriesPrefix(seriesNum) {
    return seriesNum.replace(/[a-z]+$/i, '').replace(/0+$/, '').toLowerCase();
  }

  function matchesAmdWhitelist(cpu, entries) {
    const cpuProc = (cpu.processorNumber || '').toLowerCase().trim();
    if (!cpuProc) return false;

    const cpuName = cpu.name.toLowerCase();
    // Normalize: remove ™/® symbols and extra spaces
    const cpuProcClean = cpuProc.replace(/[™®]/g, '').replace(/\s+/g, ' ').trim();
    const procTokens = cpuProcClean.split(' ');
    const lastToken = procTokens[procTokens.length - 1];

    for (const entry of entries) {
      const e = entry.toLowerCase().trim();
      const entryTokens = e.split(/\s+/);

      // "Ryzen Family" — matches any Ryzen processor
      if (/^(?:amd\s+)?ryzen\s+family$/.test(e)) {
        if (cpuName.includes('ryzen')) return true;
        continue;
      }

      // EPYC generation: "EPYC N00M Series" or bare "N00M Series"
      // N = family digit, M = generation digit (e.g., 9004 = EPYC 9xx4 Genoa)
      // Matches EPYC CPUs where model first digit = N and last numeric digit = M
      const epycGen = e.match(/^(?:epyc\s+)?(\d)00(\d)\s+series$/);
      if (epycGen && cpuName.includes('epyc')) {
        const numOnly = lastToken.replace(/[^0-9]/g, '');
        if (numOnly.length >= 3 && numOnly[0] === epycGen[1] && numOnly[numOnly.length - 1] === epycGen[2]) {
          return true;
        }
      }

      // Suffix match: entry matches the last N tokens of processorNumber
      // "Gold 3150C" matches "amd athlon gold 3150c" (last 2 tokens)
      if (entryTokens.length <= procTokens.length) {
        const suffix = procTokens.slice(-entryTokens.length).join(' ');
        if (suffix === e) return true;
      }

      // First-token match: entry's model number matches proc's last token
      // "2700E Processor" first token "2700e" matches proc last token "2700e"
      if (entryTokens[0] === lastToken) return true;

      // Short processorNumber (no AMD prefix): direct/word match
      if (!cpuProc.startsWith('amd')) {
        if (e === cpuProc) return true;
        if (entryTokens.includes(cpuProc)) return true;
      }

      // Series match: "Ryzen Embedded R2000 Series" → prefix "r2"
      const sm = e.match(/(\w+\d+)\s+series$/i);
      if (sm) {
        const prefix = getSeriesPrefix(sm[1]);
        if (prefix.length >= 2 && lastToken.startsWith(prefix)) return true;
      }
    }
    return false;
  }

  /**
   * Extract Intel Core generation from processor number.
   * "i5-8400"→8, "i7-12700K"→12, "m3-8100Y"→8
   */
  function extractIntelCoreGen(proc) {
    const m = proc.match(/^(?:i\d|m\d?)-?(\d+)/i);
    if (!m) return 0;
    return Math.floor(parseInt(m[1]) / 1000);
  }

  function matchesIntelWhitelist(cpu, entries) {
    const cpuName = cpu.name.toLowerCase();
    const cpuProc = (cpu.processorNumber || '').toLowerCase().trim();
    const cpuGen = extractIntelCoreGen(cpuProc);

    for (const entry of entries) {
      const e = entry.toLowerCase().trim();
      let m;

      // "Nth Generation Core iX Processors"
      m = e.match(/^(\d+)(?:th|st|nd|rd)\s+generation\s+core\s+(i\d|m)\s+processors?$/);
      if (m) {
        if (cpuGen === parseInt(m[1]) && cpuProc.startsWith(m[2])) return true;
        continue;
      }

      // "Core iX processors (Nth Generation)"
      m = e.match(/^core\s+(i\d|m)\s+processors?\s+\((\d+)(?:th|st|nd|rd)\s+generation\)$/);
      if (m) {
        if (cpuGen === parseInt(m[2]) && cpuProc.startsWith(m[1])) return true;
        continue;
      }

      // "Nth Generation Xeon Scalable Processors" or generic "Xeon Scalable Processors"
      if (/xeon\s+scalable\s+processors?/.test(e)) {
        if (cpuName.includes('xeon') && /platinum|gold|silver|bronze/.test(cpuName)) return true;
        continue;
      }

      // "Core Ultra Processors (Series N)"
      m = e.match(/^core\s+ultra\s+processors?\s+\(series\s+\d+\)$/);
      if (m) {
        if (cpuName.includes('core') && cpuName.includes('ultra')) return true;
        continue;
      }

      // "Core Processors (Series N)" — non-Ultra new naming
      m = e.match(/^core\s+processors?\s+\(series\s+\d+\)$/);
      if (m) {
        // Match Intel Core (non-Ultra) new naming. Check name has "core" but not "ultra"
        // and not a legacy tier (i3/i5/i7/i9) to avoid matching older Core CPUs.
        if (cpuName.includes('core') && !cpuName.includes('ultra') &&
            !/\bi[3579]-/.test(cpuProc) && !/celeron|pentium|xeon|atom/.test(cpuName)) {
          return true;
        }
        continue;
      }

      // "Xeon NNN Processors for Workstation"
      m = e.match(/^xeon\s+(\d+)\s+processors?\s+for\s+workstation$/);
      if (m) {
        if (cpuName.includes('xeon') && cpuProc.startsWith(m[1])) return true;
        continue;
      }

      // "Intel NNN Processor for Desktop"
      m = e.match(/^intel\s+(\S+)\s+processor\s+for\s+desktop$/);
      if (m) {
        if (cpuProc === m[1].toLowerCase()) return true;
        continue;
      }

      // "ProductLine SERIES Series" — e.g. "Celeron G4000 Series", "Xeon W-1200 Series"
      m = e.match(/^(.+?)\s+(\S+)\s+series$/);
      if (m && /\d/.test(m[2])) {
        const productLine = m[1];
        const prefix = getSeriesPrefix(m[2]);
        if (!prefix) continue;

        const brands = ['celeron', 'pentium', 'xeon', 'atom'];
        const brand = brands.find(b => productLine.includes(b));
        if (brand) {
          if (cpuName.includes(brand) && cpuProc.startsWith(prefix)) return true;
        } else {
          // "Core Processor N300 Series" or similar
          if (cpuProc.startsWith(prefix)) return true;
        }
        continue;
      }

      // Standalone "NXXX Series" — "N100 Series", "N200 Series", "U300 series"
      m = e.match(/^([a-z]?\d+)\s+series$/i);
      if (m) {
        const prefix = getSeriesPrefix(m[1]);
        if (prefix.length >= 2 && cpuProc.startsWith(prefix)) return true;
        continue;
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

    // CPU Whitelist check (strict — no fallback heuristic)
    const cpuWl = os.additionalRequirements?.cpuWhitelist;
    if (cpuWl) {
      if (!isOnCpuWhitelist(cpu, cpuWl.dataFile)) {
        status = 'fail';
        reasons.push(`Not on ${os.name} supported CPU list`);
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

    // CPU Whitelist check (strict — no fallback heuristic)
    const cpuWl = os.additionalRequirements?.cpuWhitelist;
    if (cpuWl) {
      if (isOnCpuWhitelist(cpu, cpuWl.dataFile)) {
        checks.push({ name: 'CPU Whitelist', status: 'pass', detail: `CPU is on ${os.name} supported list` });
      } else {
        overall = 'fail';
        checks.push({ name: 'CPU Whitelist', status: 'fail', detail: `Not on ${os.name} supported CPU list` });
      }
    }

    return { overall, checks };
  }

  /**
   * Fuzzy search OS entries by query string.
   */
  function searchOs(query, limit = 20) {
    if (!query || query.length < 2) return [];

    const osList = DataLoader.getOsRequirements();
    const q = query.toLowerCase().replace(/\s+/g, ' ').trim();
    const terms = q.split(' ');

    const scored = [];
    for (const os of osList) {
      const nameL = os.name.toLowerCase();
      const vendorL = (os.vendor || '').toLowerCase();
      const idL = os.id.toLowerCase();

      let score = 0;

      // Exact name match
      if (nameL === q) {
        score += 100;
      } else if (nameL.includes(q)) {
        score += 50;
      }

      // ID match (e.g. "rhel-9", "win11")
      if (idL.includes(q)) {
        score += 30;
      }

      // Vendor match
      if (vendorL.includes(q)) {
        score += 20;
      }

      // Term-by-term matching
      let allTermsMatch = true;
      for (const term of terms) {
        if (nameL.includes(term) || vendorL.includes(term) || idL.includes(term)) {
          score += 10;
        } else {
          allTermsMatch = false;
        }
      }
      if (allTermsMatch && terms.length > 1) {
        score += 20;
      }

      if (score > 0) {
        scored.push({ os, score });
      }
    }

    scored.sort((a, b) => b.score - a.score || a.os.name.localeCompare(b.os.name));
    return scored.slice(0, limit).map(s => s.os);
  }

  return { checkCompatibility, findCompatibleOs, findCompatibleCpus, searchCpus, searchOs, isOnCpuWhitelist, detailedCheck };
})();
