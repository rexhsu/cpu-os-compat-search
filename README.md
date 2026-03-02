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
- 3,300+ Intel/AMD CPUs (including Ryzen Embedded V1000/R1000/V2000/R2000/V3000 series), 15 operating systems

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

- **CPU specs (Intel/AMD desktop, mobile, server)**: [felixsteinke/cpu-spec-dataset](https://github.com/felixsteinke/cpu-spec-dataset)
- **AMD Ryzen Embedded V1000 series**: [AMD V1000 Series](https://www.amd.com/en/products/embedded/ryzen/ryzen-v1000-series.html) · [WikiChip V1807B](https://en.wikichip.org/wiki/amd/ryzen_embedded/v1807b) · [technical.city V1500B](https://technical.city/en/cpu/Ryzen-Embedded-V1500B)
- **AMD Ryzen Embedded R1000 series**: [AMD R1000 Series](https://www.amd.com/en/products/embedded/ryzen/ryzen-r1000-series.html) · [WikiChip R1606G](https://en.wikichip.org/wiki/amd/ryzen_embedded/r1606g) · [CNX Software R1102G/R1305G](https://www.cnx-software.com/2020/02/26/amd-goes-low-power-with-6w-ryzen-embedded-r1102g-10w-ryzen-embedded-r1305g-processors/)
- **AMD Ryzen Embedded V2000 series**: [AMD V2000 Series](https://www.amd.com/en/products/embedded/ryzen/ryzen-v2000-series.html) · [WikiChip V2718](https://en.wikichip.org/wiki/amd/ryzen_embedded/v2718) · [WikiChip V2516](https://en.wikichip.org/wiki/amd/ryzen_embedded/v2516)
- **AMD Ryzen Embedded R2000 series**: [AMD R2000 Series](https://www.amd.com/en/products/embedded/ryzen/ryzen-r2000-series.html) · [AnandTech R2000 Launch](https://www.anandtech.com/show/17460/amd-updates-ryzen-embedded-series-r2000-series-with-up-to-four-cores-and-eight-threads)
- **AMD Ryzen Embedded V3000 series**: [AMD V3000 Series](https://www.amd.com/en/products/embedded/ryzen/ryzen-v3000-series.html) · [AMD V3000 Product Brief (PDF)](https://www.amd.com/content/dam/amd/en/documents/products/embedded/ryzen/ryzen-embedded-v3000-series-product-brief.pdf)
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
