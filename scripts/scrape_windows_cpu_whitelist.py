#!/usr/bin/env python3
"""
Scrape Windows supported CPU lists from Microsoft Learn pages.
Produces per-version whitelist JSON files for CPU compatibility checking.

Usage:
    python scrape_windows_cpu_whitelist.py              # Scrape all versions
    python scrape_windows_cpu_whitelist.py --version win10-22h2  # Scrape one version
"""

import argparse
import json
import os
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# Each version maps to its Microsoft Learn URLs for Intel/AMD/Qualcomm supported CPUs.
WHITELIST_VERSIONS = {
    "win10-22h2": {
        "label": "Windows 10 22H2",
        "intel": "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-10-22h2-supported-intel-processors",
        "amd": "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-10-22h2-supported-amd-processors",
        "qualcomm": "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-10-22h2-supported-qualcomm-processors",
    },
    "win11-24h2": {
        "label": "Windows 11 24H2",
        "intel": "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-24h2-supported-intel-processors",
        "amd": "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-24h2-supported-amd-processors",
        "qualcomm": "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-24h2-supported-qualcomm-processors",
    },
    "win11-25h2": {
        "label": "Windows 11 25H2",
        "intel": "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-25h2-supported-intel-processors",
        "amd": "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-25h2-supported-amd-processors",
        "qualcomm": "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-25h2-supported-qualcomm-processors",
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_page(url: str) -> str:
    print(f"  Fetching {url}...")
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.text


def extract_entries_from_tables(html: str) -> list:
    """Extract CPU entries from HTML tables on Microsoft Learn pages.

    Table formats vary by version:
      Intel:  Manufacturer | Product Name | Series
      AMD:    Manufacturer | Brand | Model
      25H2:   Manufacturer | Product Name | Series | Exception  (4 columns)

    Strategy: detect the header row to find the "Series" or "Model" column index.
    Falls back to the last meaningful column if headers aren't found.
    """
    soup = BeautifulSoup(html, "lxml")
    entries = []

    HEADER_KEYWORDS = {"series", "model", "processor", "type", "brand",
                       "manufacturer", "product name", "exception"}

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        # Detect target column from header row
        target_col = None
        header_cells = rows[0].find_all(["th", "td"])
        headers = [c.get_text(strip=True).lower() for c in header_cells]

        # Prefer "Series" column, then "Model" column
        for preferred in ("series", "model"):
            if preferred in headers:
                target_col = headers.index(preferred)
                break

        # If no known header found, use last column
        if target_col is None:
            target_col = len(header_cells) - 1

        # Extract from data rows
        for row in rows[1:]:  # skip header row
            cells = row.find_all(["td", "th"])
            if len(cells) <= target_col:
                continue

            text = cells[target_col].get_text(strip=True)

            if not text or len(text) < 2:
                continue
            if text.lower() in HEADER_KEYWORDS:
                continue

            entries.append(text)

    return entries


def extract_cpu_names_from_lists(html: str) -> list:
    """Extract CPU names from list items as fallback."""
    soup = BeautifulSoup(html, "lxml")
    cpus = []

    content = soup.find("main") or soup.find("article") or soup
    for li in content.find_all("li"):
        text = li.get_text(strip=True)
        if re.search(
            r"(Core|Xeon|Pentium|Celeron|Atom|Ryzen|EPYC|Athlon|Threadripper|Snapdragon)",
            text, re.IGNORECASE
        ):
            cpus.append(text)

    return cpus


def normalize_entries(raw_entries: list) -> list:
    """Normalize CPU entries: deduplicate, strip, filter junk."""
    normalized = []
    for entry in raw_entries:
        entry = entry.strip()
        if not entry or len(entry) < 2:
            continue
        # Skip header-like entries
        if any(entry.lower().startswith(w) for w in
               ["model", "processor", "series", "type", "brand", "generation", "manufacturer"]):
            continue
        normalized.append(entry)
    return sorted(set(normalized))


def scrape_vendor(url: str) -> list:
    """Scrape a single vendor page and return normalized entries."""
    try:
        html = fetch_page(url)
        entries = extract_entries_from_tables(html)
        if len(entries) < 5:
            entries += extract_cpu_names_from_lists(html)
        return normalize_entries(entries)
    except Exception as e:
        print(f"  Warning: Failed to fetch {url}: {e}")
        return []


def scrape_version(slug: str, config: dict, output_dir: str):
    """Scrape all vendors for a single Windows version."""
    print(f"\n{'='*60}")
    print(f"Scraping {config['label']} ({slug})")
    print(f"{'='*60}")

    intel_cpus = scrape_vendor(config["intel"])
    print(f"  Found {len(intel_cpus)} Intel entries")

    amd_cpus = scrape_vendor(config["amd"])
    print(f"  Found {len(amd_cpus)} AMD entries")

    qualcomm_cpus = scrape_vendor(config["qualcomm"])
    print(f"  Found {len(qualcomm_cpus)} Qualcomm entries")

    data = {
        "metadata": {
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": f"Microsoft Learn - {config['label']} supported processors",
            "intelUrl": config["intel"],
            "amdUrl": config["amd"],
            "qualcommUrl": config["qualcomm"],
            "counts": {
                "intel": len(intel_cpus),
                "amd": len(amd_cpus),
                "qualcomm": len(qualcomm_cpus),
            },
        },
        "intel": intel_cpus,
        "amd": amd_cpus,
        "qualcomm": qualcomm_cpus,
    }

    filename = f"windows-cpu-whitelist-{slug}.json"
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = len(intel_cpus) + len(amd_cpus) + len(qualcomm_cpus)
    print(f"  Generated {filename} with {total} total entries")


def main():
    parser = argparse.ArgumentParser(description="Scrape Windows supported CPU lists")
    parser.add_argument(
        "--version",
        choices=list(WHITELIST_VERSIONS.keys()),
        help="Scrape only this version (default: all)",
    )
    args = parser.parse_args()

    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)

    if args.version:
        versions = {args.version: WHITELIST_VERSIONS[args.version]}
    else:
        versions = WHITELIST_VERSIONS

    for slug, config in versions.items():
        scrape_version(slug, config, output_dir)

    print(f"\nDone. Scraped {len(versions)} version(s).")


if __name__ == "__main__":
    main()
