#!/usr/bin/env python3
"""Generate OS requirements JSON from manually curated data."""

import json
import os
from datetime import datetime, timezone

OS_REQUIREMENTS = [
    {
        "id": "windows-11-22h2",
        "name": "Windows 11 22H2",
        "vendor": "Microsoft",
        "type": "desktop",
        "releaseDate": "2022-09",
        "eol": "2025-10",
        "x86_64_level": 2,
        "minRamGB": 4,
        "minStorageGB": 64,
        "additionalRequirements": {
            "tpm2": True,
            "uefi": True,
            "secureBootCapable": True,
            "cpuWhitelist": {
                "dataFile": "windows-cpu-whitelist-win11-22h2.json",
                "enforcement": "fail"
            }
        },
        "requiredFeatures": ["sse42", "popcnt"],
        "notes": "Requires TPM 2.0, UEFI Secure Boot, and CPU must be on Microsoft's supported list."
    },
    {
        "id": "windows-11-23h2",
        "name": "Windows 11 23H2",
        "vendor": "Microsoft",
        "type": "desktop",
        "releaseDate": "2023-10",
        "eol": "2025-11",
        "x86_64_level": 2,
        "minRamGB": 4,
        "minStorageGB": 64,
        "additionalRequirements": {
            "tpm2": True,
            "uefi": True,
            "secureBootCapable": True,
            "cpuWhitelist": {
                "dataFile": "windows-cpu-whitelist-win11-22h2.json",
                "enforcement": "fail"
            }
        },
        "requiredFeatures": ["sse42", "popcnt"],
        "notes": "Requires TPM 2.0, UEFI Secure Boot, and CPU must be on Microsoft's supported list. Shares CPU list with 22H2."
    },
    {
        "id": "windows-11-24h2",
        "name": "Windows 11 24H2",
        "vendor": "Microsoft",
        "type": "desktop",
        "releaseDate": "2024-10",
        "eol": "2026-10",
        "x86_64_level": 2,
        "minRamGB": 4,
        "minStorageGB": 64,
        "additionalRequirements": {
            "tpm2": True,
            "uefi": True,
            "secureBootCapable": True,
            "cpuWhitelist": {
                "dataFile": "windows-cpu-whitelist-win11-24h2.json",
                "enforcement": "fail"
            }
        },
        "requiredFeatures": ["sse42", "popcnt"],
        "notes": "Requires TPM 2.0, UEFI Secure Boot, and CPU must be on Microsoft's supported list."
    },
    {
        "id": "windows-11-25h2",
        "name": "Windows 11 25H2",
        "vendor": "Microsoft",
        "type": "desktop",
        "releaseDate": "2025-10",
        "eol": "2027-10",
        "x86_64_level": 2,
        "minRamGB": 4,
        "minStorageGB": 64,
        "additionalRequirements": {
            "tpm2": True,
            "uefi": True,
            "secureBootCapable": True,
            "cpuWhitelist": {
                "dataFile": "windows-cpu-whitelist-win11-25h2.json",
                "enforcement": "fail"
            }
        },
        "requiredFeatures": ["sse42", "popcnt"],
        "notes": "Requires TPM 2.0, UEFI Secure Boot, and CPU must be on Microsoft's supported list."
    },
    {
        "id": "windows-10-22h2",
        "name": "Windows 10 22H2",
        "vendor": "Microsoft",
        "type": "desktop",
        "releaseDate": "2022-10",
        "eol": "2025-10",
        "x86_64_level": 1,
        "minRamGB": 2,
        "minStorageGB": 32,
        "additionalRequirements": {
            "cpuWhitelist": {
                "dataFile": "windows-cpu-whitelist-win10-22h2.json",
                "enforcement": "fail"
            }
        },
        "requiredFeatures": [],
        "notes": "End of support October 2025. CPU must be on Microsoft's supported list."
    },
    {
        "id": "windows-10-ltsc-2021",
        "name": "Windows 10 Enterprise LTSC 2021",
        "vendor": "Microsoft",
        "type": "desktop",
        "releaseDate": "2021-11",
        "eol": "2027-01",
        "x86_64_level": 1,
        "minRamGB": 2,
        "minStorageGB": 32,
        "additionalRequirements": {
            "cpuWhitelist": {
                "dataFile": "windows-cpu-whitelist-win10-21h2.json",
                "enforcement": "fail"
            }
        },
        "requiredFeatures": [],
        "notes": "Long-Term Servicing Channel. CPU must be on Microsoft's supported list."
    },
    {
        "id": "windows-10-ltsc-1809",
        "name": "Windows 10 Enterprise LTSC 1809",
        "vendor": "Microsoft",
        "type": "desktop",
        "releaseDate": "2018-11",
        "eol": "2029-01",
        "x86_64_level": 1,
        "minRamGB": 2,
        "minStorageGB": 32,
        "additionalRequirements": {
            "cpuWhitelist": {
                "dataFile": "windows-cpu-whitelist-win10-1809.json",
                "enforcement": "fail"
            }
        },
        "requiredFeatures": [],
        "notes": "Long-Term Servicing Channel. CPU must be on Microsoft's supported list."
    },
    {
        "id": "windows-server-2025",
        "name": "Windows Server 2025",
        "vendor": "Microsoft",
        "type": "server",
        "releaseDate": "2024-11",
        "eol": "2034-10",
        "x86_64_level": 2,
        "minRamGB": 0.5,
        "minRamGBDesktop": 2,
        "minStorageGB": 32,
        "additionalRequirements": {
            "slat": True,
            "cpuWhitelist": {
                "dataFile": "windows-cpu-whitelist-server-2025.json",
                "enforcement": "fail"
            }
        },
        "requiredFeatures": ["sse42", "popcnt"],
        "notes": "512 MB RAM (Core), 2 GB (Desktop Experience). Requires SLAT. CPU must be on Microsoft's supported list."
    },
    {
        "id": "windows-server-2022",
        "name": "Windows Server 2022",
        "vendor": "Microsoft",
        "type": "server",
        "releaseDate": "2021-08",
        "eol": "2031-10",
        "x86_64_level": 1,
        "minRamGB": 0.5,
        "minRamGBDesktop": 2,
        "minStorageGB": 32,
        "additionalRequirements": {
            "slat": True,
            "cpuWhitelist": {
                "dataFile": "windows-cpu-whitelist-server-2022.json",
                "enforcement": "fail"
            }
        },
        "requiredFeatures": [],
        "notes": "512 MB RAM (Core), 2 GB (Desktop Experience). Requires SLAT. CPU must be on Microsoft's supported list."
    },
    {
        "id": "windows-server-2019",
        "name": "Windows Server 2019",
        "vendor": "Microsoft",
        "type": "server",
        "releaseDate": "2018-10",
        "eol": "2029-01",
        "x86_64_level": 1,
        "minRamGB": 0.5,
        "minRamGBDesktop": 2,
        "minStorageGB": 32,
        "additionalRequirements": {
            "cpuWhitelist": {
                "dataFile": "windows-cpu-whitelist-server-2019.json",
                "enforcement": "fail"
            }
        },
        "requiredFeatures": [],
        "notes": "512 MB RAM (Core), 2 GB (Desktop Experience). CPU must be on Microsoft's supported list."
    },
    {
        "id": "rhel-10",
        "name": "Red Hat Enterprise Linux 10",
        "vendor": "Red Hat",
        "type": "server",
        "releaseDate": "2025-05",
        "eol": "2035-05",
        "x86_64_level": 3,
        "minRamGB": 1.5,
        "minStorageGB": 10,
        "additionalRequirements": {},
        "requiredFeatures": ["sse42", "popcnt", "avx", "avx2", "bmi1", "bmi2", "fma"],
        "notes": "Requires x86-64-v3: AVX, AVX2, BMI1, BMI2, FMA, and more."
    },
    {
        "id": "rhel-9",
        "name": "Red Hat Enterprise Linux 9",
        "vendor": "Red Hat",
        "type": "server",
        "releaseDate": "2022-05",
        "eol": "2032-05",
        "x86_64_level": 2,
        "minRamGB": 1.5,
        "minStorageGB": 10,
        "additionalRequirements": {},
        "requiredFeatures": ["sse42", "popcnt"],
        "notes": "Requires x86-64-v2: SSE4.2, POPCNT, CMPXCHG16B, and LAHF/SAHF."
    },
    {
        "id": "rhel-8",
        "name": "Red Hat Enterprise Linux 8",
        "vendor": "Red Hat",
        "type": "server",
        "releaseDate": "2019-05",
        "eol": "2029-05",
        "x86_64_level": 1,
        "minRamGB": 2,
        "minStorageGB": 10,
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "Basic x86-64 requirements."
    },
    {
        "id": "ubuntu-24.04",
        "name": "Ubuntu 24.04 LTS",
        "vendor": "Canonical",
        "type": "desktop",
        "releaseDate": "2024-04",
        "eol": "2029-04",
        "x86_64_level": 1,
        "minRamGB": 4,
        "minRamGBServer": 1.5,
        "minStorageGB": 25,
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "4 GB RAM (Desktop), 1.5 GB (Server minimal)."
    },
    {
        "id": "ubuntu-22.04",
        "name": "Ubuntu 22.04 LTS",
        "vendor": "Canonical",
        "type": "desktop",
        "releaseDate": "2022-04",
        "eol": "2027-04",
        "x86_64_level": 1,
        "minRamGB": 4,
        "minRamGBServer": 1,
        "minStorageGB": 25,
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "4 GB RAM (Desktop), 1 GB (Server minimal)."
    },
    {
        "id": "debian-12",
        "name": "Debian 12 (Bookworm)",
        "vendor": "Debian",
        "type": "server",
        "releaseDate": "2023-06",
        "eol": "2028-06",
        "x86_64_level": 1,
        "minRamGB": 0.5,
        "minStorageGB": 10,
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "512 MB RAM minimum. Very lightweight requirements."
    },
    {
        "id": "debian-11",
        "name": "Debian 11 (Bullseye)",
        "vendor": "Debian",
        "type": "server",
        "releaseDate": "2021-08",
        "eol": "2026-08",
        "x86_64_level": 1,
        "minRamGB": 0.5,
        "minStorageGB": 10,
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "512 MB RAM minimum."
    },
    {
        "id": "centos-stream-9",
        "name": "CentOS Stream 9",
        "vendor": "Red Hat",
        "type": "server",
        "releaseDate": "2021-12",
        "eol": "2027-05",
        "x86_64_level": 2,
        "minRamGB": 2,
        "minStorageGB": 10,
        "additionalRequirements": {},
        "requiredFeatures": ["sse42", "popcnt"],
        "notes": "Requires x86-64-v2. Rolling-release ahead of RHEL 9."
    },
    {
        "id": "fedora-41",
        "name": "Fedora 41",
        "vendor": "Red Hat",
        "type": "desktop",
        "releaseDate": "2024-10",
        "eol": "2025-11",
        "x86_64_level": 1,
        "minRamGB": 2,
        "minStorageGB": 20,
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "Basic x86-64 requirements. Short support cycle."
    },
    {
        "id": "rocky-10",
        "name": "Rocky Linux 10",
        "vendor": "Rocky Enterprise Software Foundation",
        "type": "server",
        "releaseDate": "2025-07",
        "eol": "2035-05",
        "x86_64_level": 3,
        "minRamGB": 1.5,
        "minStorageGB": 10,
        "additionalRequirements": {},
        "requiredFeatures": ["sse42", "popcnt", "avx", "avx2", "bmi1", "bmi2", "fma"],
        "notes": "RHEL 10 compatible rebuild. Requires x86-64-v3: AVX, AVX2, BMI1, BMI2, FMA."
    },
    {
        "id": "rocky-9",
        "name": "Rocky Linux 9",
        "vendor": "Rocky Enterprise Software Foundation",
        "type": "server",
        "releaseDate": "2022-07",
        "eol": "2032-05",
        "x86_64_level": 2,
        "minRamGB": 1.5,
        "minStorageGB": 10,
        "additionalRequirements": {},
        "requiredFeatures": ["sse42", "popcnt"],
        "notes": "RHEL 9 compatible rebuild. Requires x86-64-v2: SSE4.2, POPCNT."
    },
    {
        "id": "oracle-linux-10",
        "name": "Oracle Linux 10",
        "vendor": "Oracle",
        "type": "server",
        "releaseDate": "2025-07",
        "eol": "2035-07",
        "x86_64_level": 3,
        "minRamGB": 1.5,
        "minStorageGB": 10,
        "additionalRequirements": {},
        "requiredFeatures": ["sse42", "popcnt", "avx", "avx2", "bmi1", "bmi2", "fma"],
        "notes": "RHEL 10 compatible. Requires x86-64-v3: AVX, AVX2, BMI1, BMI2, FMA."
    },
    {
        "id": "oracle-linux-9",
        "name": "Oracle Linux 9",
        "vendor": "Oracle",
        "type": "server",
        "releaseDate": "2022-07",
        "eol": "2032-07",
        "x86_64_level": 2,
        "minRamGB": 1.5,
        "minStorageGB": 10,
        "additionalRequirements": {},
        "requiredFeatures": ["sse42", "popcnt"],
        "notes": "RHEL 9 compatible. Requires x86-64-v2: SSE4.2, POPCNT."
    },
    {
        "id": "sles-15-sp7",
        "name": "SUSE Linux Enterprise Server 15 SP7",
        "vendor": "SUSE",
        "type": "server",
        "releaseDate": "2025-06",
        "eol": "2031-07",
        "x86_64_level": 1,
        "minRamGB": 1,
        "minStorageGB": 12,
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "Basic x86-64 requirements. 1 GB RAM minimum for text mode, 1.5 GB recommended."
    },
    {
        "id": "ubuntu-core-24",
        "name": "Ubuntu Core 24",
        "vendor": "Canonical",
        "type": "iot",
        "releaseDate": "2024-06",
        "eol": "2036-06",
        "x86_64_level": 1,
        "minRamGB": 0.512,
        "minStorageGB": 4,
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "Minimal IoT/embedded OS. 512 MB RAM, 4 GB storage minimum. 12-year LTS support."
    },
    {
        "id": "freebsd-14",
        "name": "FreeBSD 14",
        "vendor": "FreeBSD Project",
        "type": "server",
        "releaseDate": "2023-11",
        "eol": "2028-11",
        "x86_64_level": 1,
        "minRamGB": 0.128,
        "minStorageGB": 1.5,
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "128 MB RAM minimum (more for GUI). Basic amd64 requirements. Very lightweight."
    },
    {
        "id": "oracle-solaris-11.4",
        "name": "Oracle Solaris 11.4",
        "vendor": "Oracle",
        "type": "server",
        "releaseDate": "2018-08",
        "eol": "2034-11",
        "x86_64_level": 1,
        "minRamGB": 2,
        "minStorageGB": 13,
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "Requires x86-64 CPU. 2 GB RAM minimum (4 GB recommended). Refer to Oracle HCL for certified hardware."
    }
]


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)

    data = {
        "metadata": {
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "Manual curation from official OS documentation",
            "count": len(OS_REQUIREMENTS)
        },
        "operatingSystems": OS_REQUIREMENTS
    }

    output_path = os.path.join(output_dir, "os-requirements.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Generated {output_path} with {len(OS_REQUIREMENTS)} OS entries")


if __name__ == "__main__":
    main()
