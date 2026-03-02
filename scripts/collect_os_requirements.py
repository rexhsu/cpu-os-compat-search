#!/usr/bin/env python3
"""Generate OS requirements JSON from manually curated data."""

import json
import os
from datetime import datetime, timezone

OS_REQUIREMENTS = [
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
            "win11CpuWhitelist": True
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
            "win11CpuWhitelist": True
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
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "End of support October 2025. Basic x86-64 requirements."
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
            "slat": True
        },
        "requiredFeatures": ["sse42", "popcnt"],
        "notes": "512 MB RAM (Core), 2 GB (Desktop Experience). Requires SLAT (Second Level Address Translation)."
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
            "slat": True
        },
        "requiredFeatures": [],
        "notes": "512 MB RAM (Core), 2 GB (Desktop Experience). Requires SLAT."
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
        "additionalRequirements": {},
        "requiredFeatures": [],
        "notes": "512 MB RAM (Core), 2 GB (Desktop Experience)."
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
