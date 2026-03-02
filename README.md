# CPU / OS Compatibility Search

**Live Demo: https://rexhsu.github.io/cpu-os-compat-search/**

A static GitHub Pages web app to query CPU model compatibility with various operating systems (Windows, RHEL, Ubuntu, Debian, CentOS, Fedora, Rocky Linux, AlmaLinux, Oracle Linux, SUSE SLES, openSUSE, FreeBSD, Oracle Solaris, VMware ESXi, Proxmox VE). Checks x86-64 microarchitecture levels, CPU features, and Windows CPU whitelist requirements.

## Features

- **Search by CPU + OS**: Detailed one-to-one compatibility check with per-feature breakdown
- **Search by CPU**: Enter a CPU model name to see all compatible operating systems
- **Search by OS**: Search an OS to see all compatible CPUs
- Autocomplete search with fuzzy matching for both CPU and OS fields
- x86-64 level (v1–v4) detection from instruction set extensions
- Windows CPU whitelist checking for desktop, LTSC, and Server editions via Microsoft Learn data
- Cross-tab navigation: click any result to jump to the detailed CPU+OS check
- TPM 2.0 support inference (Intel PTT 8th gen+, AMD fTPM Zen+)
- 3,300+ Intel/AMD CPUs (including Ryzen Embedded V1000/R1000/V2000/R2000/V3000 series), 36 operating systems

## Supported Operating Systems

| OS | x86-64 Level | Min RAM | Notes |
|---|---|---|---|
| Windows 11 24H2 | v2 + whitelist | 4 GB | TPM 2.0, UEFI Secure Boot |
| Windows 11 25H2 | v2 + whitelist | 4 GB | TPM 2.0, UEFI Secure Boot |
| Windows 10 Enterprise LTSC 2021 | v1 + whitelist | 2 GB | EOL 2027-01 |
| Windows 10 Enterprise LTSC 1809 | v1 + whitelist | 2 GB | EOL 2029-01 |
| Windows Server 2025 | v2 + whitelist | 512 MB / 2 GB | SLAT required |
| Windows Server 2022 | v1 + whitelist | 512 MB / 2 GB | SLAT required |
| Windows Server 2019 | v1 + whitelist | 512 MB / 2 GB | |
| Windows Server 2016 | v1 + whitelist | 512 MB / 2 GB | Extended support until 2027-01 |
| RHEL 10 | v3 | 1.5 GB | |
| RHEL 9 | v2 | 1.5 GB | |
| RHEL 8 | v1 | 2 GB | |
| Ubuntu 24.04 LTS | v1 | 4 GB / 1.5 GB | |
| Ubuntu 22.04 LTS | v1 | 4 GB / 1 GB | |
| Debian 13 (Trixie) | v1 | 512 MB | Current stable |
| Debian 12 (Bookworm) | v1 | 512 MB | |
| CentOS Stream 10 | v3 | 1.5 GB | Rolling ahead of RHEL 10 |
| CentOS Stream 9 | v2 | 2 GB | Rolling ahead of RHEL 9 |
| Fedora 43 | v1 | 2 GB | |
| Fedora 42 | v1 | 2 GB | |
| Rocky Linux 10 | v3 | 1.5 GB | |
| Rocky Linux 9 | v2 | 1.5 GB | |
| Rocky Linux 8 | v1 | 2 GB | |
| AlmaLinux 10 | v3 | 1.5 GB | Also provides v2 arch |
| AlmaLinux 9 | v2 | 1.5 GB | |
| AlmaLinux 8 | v1 | 2 GB | |
| Oracle Linux 10 | v3 | 1.5 GB | |
| Oracle Linux 9 | v2 | 1.5 GB | |
| Oracle Linux 8 | v1 | 2 GB | |
| SUSE SLES 15 SP7 | v1 | 1 GB | |
| openSUSE Leap 16 | v2 | 1 GB | |
| Ubuntu Core 24 | v1 | 512 MB | IoT/embedded, 12-year LTS |
| FreeBSD 15 | v1 | 128 MB | |
| FreeBSD 14 | v1 | 128 MB | |
| Oracle Solaris 11.4 | v1 | 2 GB | |
| VMware ESXi 8 | v1 | 8 GB | Requires VT-x/AMD-V |
| Proxmox VE 9 | v1 | 2 GB | Based on Debian 13, requires VT-x/AMD-V |

## Data Sources

- **CPU specs (Intel/AMD desktop, mobile, server)**: [felixsteinke/cpu-spec-dataset](https://github.com/felixsteinke/cpu-spec-dataset)
- **AMD Ryzen Embedded V1000 series**: [AMD V1000 Series](https://www.amd.com/en/products/embedded/ryzen/ryzen-v1000-series.html) · [WikiChip V1807B](https://en.wikichip.org/wiki/amd/ryzen_embedded/v1807b) · [technical.city V1500B](https://technical.city/en/cpu/Ryzen-Embedded-V1500B)
- **AMD Ryzen Embedded R1000 series**: [AMD R1000 Series](https://www.amd.com/en/products/embedded/ryzen/ryzen-r1000-series.html) · [WikiChip R1606G](https://en.wikichip.org/wiki/amd/ryzen_embedded/r1606g) · [CNX Software R1102G/R1305G](https://www.cnx-software.com/2020/02/26/amd-goes-low-power-with-6w-ryzen-embedded-r1102g-10w-ryzen-embedded-r1305g-processors/)
- **AMD Ryzen Embedded V2000 series**: [AMD V2000 Series](https://www.amd.com/en/products/embedded/ryzen/ryzen-v2000-series.html) · [WikiChip V2718](https://en.wikichip.org/wiki/amd/ryzen_embedded/v2718) · [WikiChip V2516](https://en.wikichip.org/wiki/amd/ryzen_embedded/v2516)
- **AMD Ryzen Embedded R2000 series**: [AMD R2000 Series](https://www.amd.com/en/products/embedded/ryzen/ryzen-r2000-series.html) · [AnandTech R2000 Launch](https://www.anandtech.com/show/17460/amd-updates-ryzen-embedded-series-r2000-series-with-up-to-four-cores-and-eight-threads)
- **AMD Ryzen Embedded V3000 series**: [AMD V3000 Series](https://www.amd.com/en/products/embedded/ryzen/ryzen-v3000-series.html) · [AMD V3000 Product Brief (PDF)](https://www.amd.com/content/dam/amd/en/documents/products/embedded/ryzen/ryzen-embedded-v3000-series-product-brief.pdf)
- **Windows CPU whitelists**: [Microsoft Learn - Processor Requirements](https://learn.microsoft.com/en-us/windows-hardware/design/minimum/windows-processor-requirements) (desktop, LTSC, and Server editions)
- **OS requirements**: Official documentation (manually curated)
  - [Windows supported processors](https://aka.ms/CPUlist)
  - [Ubuntu system requirements](https://help.ubuntu.com/community/Installation/SystemRequirements) · [Server](https://documentation.ubuntu.com/server/reference/installation/system-requirements/) · [Core](https://documentation.ubuntu.com/core/reference/system-requirements/)
  - [Debian hardware requirements](https://www.debian.org/releases/stable/amd64/ch03s04.en.html)
  - [RHEL architecture requirements](https://access.redhat.com/zh_CN/articles/3482381)
  - [Rocky Linux minimum hardware](https://docs.rockylinux.org/10/guides/minimum_hardware_requirements/)
  - [CentOS product info](https://wiki.centos.org/About/Product.html)
  - [Fedora hardware overview](https://docs.fedoraproject.org/en-US/fedora/latest/release-notes/hardware_overview/)
  - [Oracle Linux release notes](https://docs.oracle.com/en/operating-systems/oracle-linux/9/relnotes9.3/) · [HCL](https://linux.oracle.com/hardware-certifications)
  - [SUSE SLES deployment guide](https://documentation.suse.com/sles/15-SP7/html/SLES-all/cha-x86.html) · [YES HW database](https://www.suse.com/yessearch/)
  - [FreeBSD handbook](https://docs.freebsd.org/en/books/handbook/bsdinstall/) · [Release notes](https://www.freebsd.org/releases/)
  - [AlmaLinux release notes](https://wiki.almalinux.org/release-notes/)
  - [openSUSE Leap requirements](https://get.opensuse.org/leap/)
  - [VMware ESXi hardware requirements](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/8-0/esxi-upgrade-8-0/upgrading-esxi-hosts-upgrade/esxi-requirements-upgrade/esxi-hardware-requirements-upgrade.html)
  - [Proxmox VE requirements](https://www.proxmox.com/en/products/proxmox-virtual-environment/requirements)
  - [Oracle Solaris HCL](https://www.oracle.com/webfolder/technetwork/hcl/index.html) · [Install guide](https://docs.oracle.com/cd/E37838_01/html/E60973/glmru.html)

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
