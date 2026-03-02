#!/usr/bin/env python3
"""Generate Windows Server CPU whitelist JSON files.

Unlike desktop Windows, Server editions don't have separate per-vendor CPU list pages.
CPU support data is manually curated from the main processor requirements page:
https://learn.microsoft.com/en-us/windows-hardware/design/minimum/windows-processor-requirements
"""

import json
import os
from datetime import datetime, timezone

SOURCE_URL = "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/windows-processor-requirements"

# Helper: generate "Nth Generation Core i3 Processors" entries for gen range
def _core_i3_gens(start, end):
    """Generate Core i3 generation entries from start to end (inclusive)."""
    ordinals = {1: "1st", 2: "2nd", 3: "3rd"}
    entries = []
    for n in range(start, end + 1):
        suffix = ordinals.get(n, f"{n}th")
        entries.append(f"{suffix} Generation Core i3 Processors")
    return entries


SERVER_WHITELISTS = {
    "server-2019": {
        "label": "Windows Server 2019",
        "intel": [
            # Core i3 up through 13th generation
            *_core_i3_gens(1, 13),
            # Pentium
            "Pentium G5000 Series",
            "Pentium G7400 Series",
            # Celeron
            "Celeron G4900 Series",
            # Xeon Scalable (1st through 5th gen)
            "1st Generation Xeon Scalable Processors",
            "2nd Generation Xeon Scalable Processors",
            "3rd Generation Xeon Scalable Processors",
            "4th Generation Xeon Scalable Processors",
            "5th Generation Xeon Scalable Processors",
            # Xeon E series (E-2100 through E-2400)
            "Xeon E-2100 Series",
            "Xeon E-2200 Series",
            "Xeon E-2300 Series",
            "Xeon E-2400 Series",
            # Xeon D series
            "Xeon D-1500 Series",
            "Xeon D-1700 Series",
            "Xeon D-2100 Series",
            "Xeon D-2700 Series",
            # Atom
            "Atom C3300 Series",
        ],
        "amd": [
            # Legacy AMD families (7th gen)
            "A9-9000 Series",
            "E2-9000 Series",
            "FX-9000 Series",
            # Ryzen (all families)
            "Ryzen Family",
            # EPYC generations
            "EPYC 7001 Series",
            "EPYC 7002 Series",
            "EPYC 7003 Series",
            "EPYC 8004 Series",
            "EPYC 9004 Series",
            "EPYC 9005 Series",
        ],
    },
    "server-2022": {
        "label": "Windows Server 2022",
        "intel": [
            # Core i3 up through 13th generation
            *_core_i3_gens(1, 13),
            # Pentium
            "Pentium G5000 Series",
            "Pentium G7400 Series",
            # Celeron
            "Celeron G4900 Series",
            # Xeon Scalable (1st through 5th gen)
            "1st Generation Xeon Scalable Processors",
            "2nd Generation Xeon Scalable Processors",
            "3rd Generation Xeon Scalable Processors",
            "4th Generation Xeon Scalable Processors",
            "5th Generation Xeon Scalable Processors",
            # Xeon 6
            "Xeon 6900P Series",
            "Xeon 6700E Series",
            "Xeon 6700P Series",
            "Xeon 6500P Series",
            "Xeon 6300P Series",
            # Xeon E series
            "Xeon E-2300 Series",
            "Xeon E-2400 Series",
            # Xeon D series
            "Xeon D-1700 Series",
            "Xeon D-2100 Series",
            "Xeon D-2700 Series",
            # Atom
            "Atom C3300 Series",
        ],
        "amd": [
            # Legacy AMD families (7th gen)
            "A9-9000 Series",
            "E2-9000 Series",
            "FX-9000 Series",
            # Ryzen (all families)
            "Ryzen Family",
            # EPYC generations
            "EPYC 7001 Series",
            "EPYC 7002 Series",
            "EPYC 7003 Series",
            "EPYC 4004 Series",
            "EPYC 4005 Series",
            "EPYC 8004 Series",
            "EPYC 9004 Series",
            "EPYC 9005 Series",
        ],
    },
    "server-2025": {
        "label": "Windows Server 2025",
        "intel": [
            # No Core processors for Server 2025
            # Pentium (only G7400/G7400T)
            "Pentium G7400 Series",
            # Xeon Scalable (2nd through 5th gen — no 1st gen)
            "2nd Generation Xeon Scalable Processors",
            "3rd Generation Xeon Scalable Processors",
            "4th Generation Xeon Scalable Processors",
            "5th Generation Xeon Scalable Processors",
            # Xeon 6
            "Xeon 6900P Series",
            "Xeon 6700E Series",
            "Xeon 6700P Series",
            "Xeon 6500P Series",
            "Xeon 6300P Series",
            # Xeon E series
            "Xeon E-2300 Series",
            "Xeon E-2400 Series",
            # Xeon D series
            "Xeon D-1700 Series",
            "Xeon D-1800 Series",
            "Xeon D-2100 Series",
            "Xeon D-2700 Series",
            "Xeon D-2800 Series",
        ],
        "amd": [
            # EPYC only (no Ryzen for Server 2025)
            "EPYC 7002 Series",
            "EPYC 7003 Series",
            "EPYC 4004 Series",
            "EPYC 4005 Series",
            "EPYC 8004 Series",
            "EPYC 9004 Series",
            "EPYC 9005 Series",
        ],
    },
}


def generate_whitelist(slug, config, output_dir):
    """Generate a single server whitelist JSON file."""
    data = {
        "metadata": {
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": f"Microsoft Learn - {config['label']} processor requirements (manually curated)",
            "sourceUrl": SOURCE_URL,
            "counts": {
                "intel": len(config["intel"]),
                "amd": len(config["amd"]),
                "qualcomm": 0,
            },
        },
        "intel": sorted(config["intel"]),
        "amd": sorted(config["amd"]),
        "qualcomm": [],
    }

    filename = f"windows-cpu-whitelist-{slug}.json"
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = len(config["intel"]) + len(config["amd"])
    print(f"Generated {filename} with {total} entries ({len(config['intel'])} Intel + {len(config['amd'])} AMD)")


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)

    for slug, config in SERVER_WHITELISTS.items():
        generate_whitelist(slug, config, output_dir)

    print(f"\nDone. Generated {len(SERVER_WHITELISTS)} server whitelist files.")


if __name__ == "__main__":
    main()
