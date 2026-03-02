# CPU / OS Compatibility Search

**Live Demo: https://rexhsu.github.io/cpu-os-compat-search/**

A static GitHub Pages web app to query CPU model compatibility with various operating systems (Windows, RHEL, Ubuntu, Debian, CentOS, Fedora). Checks x86-64 microarchitecture levels, CPU features, and Windows 11 whitelist requirements.

## Features

- **Search by CPU**: Enter a CPU model name to see which operating systems it's compatible with
- **Search by OS**: Select an OS to see which CPUs are compatible
- Autocomplete CPU search with fuzzy matching
- x86-64 level (v1–v4) detection from instruction set extensions
- Windows 11 CPU whitelist checking via Microsoft Learn data
- TPM 2.0 support inference (Intel PTT 8th gen+, AMD fTPM Zen+)
- 3,300+ Intel/AMD CPUs, 15 operating systems

## Supported Operating Systems

| OS | x86-64 Level | Min RAM |
|---|---|---|
| Windows 11 24H2/25H2 | v2 + whitelist | 4 GB |
| Windows 10 22H2 | v1 | 2 GB |
| Windows Server 2025 | v2 | 512 MB / 2 GB |
| Windows Server 2022 | v1 | 512 MB / 2 GB |
| Windows Server 2019 | v1 | 512 MB / 2 GB |
| RHEL 10 | v3 | 1.5 GB |
| RHEL 9 | v2 | 1.5 GB |
| RHEL 8 | v1 | 2 GB |
| Ubuntu 24.04 LTS | v1 | 4 GB / 1.5 GB |
| Ubuntu 22.04 LTS | v1 | 4 GB / 1 GB |
| Debian 12 | v1 | 512 MB |
| Debian 11 | v1 | 512 MB |
| CentOS Stream 9 | v2 | 2 GB |
| Fedora 41 | v1 | 2 GB |

## Data Sources

- **CPU specs**: [felixsteinke/cpu-spec-dataset](https://github.com/felixsteinke/cpu-spec-dataset)
- **Win11 whitelist**: [Microsoft Learn](https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-supported-intel-processors)
- **OS requirements**: Official documentation (manually curated)

## Development

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Build data files
python scripts/build_data.py

# Serve locally
python -m http.server 8000
```

## Updating Data

Use the "Update CPU/OS Data" GitHub Actions workflow (manual trigger) to refresh data from upstream sources.
