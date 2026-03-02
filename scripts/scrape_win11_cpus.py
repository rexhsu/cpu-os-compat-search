#!/usr/bin/env python3
"""
Scrape Windows 11 supported CPU lists from Microsoft Learn pages.
Produces a whitelist JSON for Win11 CPU compatibility checking.
"""

import json
import os
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

INTEL_URL = "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-24h2-supported-intel-processors"
AMD_URL = "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-24h2-supported-amd-processors"
QUALCOMM_URL = "https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-24h2-supported-qualcomm-processors"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_page(url: str) -> str:
    print(f"Fetching {url}...")
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.text


def extract_cpu_names_from_table(html: str) -> list:
    """Extract CPU model names from HTML tables on MS Learn pages."""
    soup = BeautifulSoup(html, "lxml")
    cpus = []

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            for cell in cells:
                text = cell.get_text(strip=True)
                if text and not text.lower().startswith(("model", "processor", "series", "type", "brand")):
                    cpus.append(text)

    return cpus


def extract_cpu_names_from_lists(html: str) -> list:
    """Extract CPU names from list items as fallback."""
    soup = BeautifulSoup(html, "lxml")
    cpus = []

    # Look for list items in the main content area
    content = soup.find("main") or soup.find("article") or soup
    for li in content.find_all("li"):
        text = li.get_text(strip=True)
        # Filter to likely CPU names
        if re.search(r"(Core|Xeon|Pentium|Celeron|Atom|Ryzen|EPYC|Athlon|Threadripper|Snapdragon)", text, re.IGNORECASE):
            cpus.append(text)

    return cpus


def normalize_intel_entries(raw_entries: list) -> list:
    """Normalize Intel CPU entries into searchable patterns."""
    normalized = []
    for entry in raw_entries:
        entry = entry.strip()
        if not entry or len(entry) < 3:
            continue
        # Skip header-like entries
        if any(entry.lower().startswith(w) for w in ["model", "processor", "series", "type", "brand", "generation"]):
            continue
        normalized.append(entry)
    return list(set(normalized))


def normalize_amd_entries(raw_entries: list) -> list:
    """Normalize AMD CPU entries."""
    normalized = []
    for entry in raw_entries:
        entry = entry.strip()
        if not entry or len(entry) < 3:
            continue
        if any(entry.lower().startswith(w) for w in ["model", "processor", "series", "type", "brand"]):
            continue
        normalized.append(entry)
    return list(set(normalized))


def main():
    intel_cpus = []
    amd_cpus = []
    qualcomm_cpus = []

    # Fetch Intel
    try:
        html = fetch_page(INTEL_URL)
        intel_cpus = extract_cpu_names_from_table(html)
        if len(intel_cpus) < 10:
            intel_cpus += extract_cpu_names_from_lists(html)
        intel_cpus = normalize_intel_entries(intel_cpus)
        print(f"  Found {len(intel_cpus)} Intel entries")
    except Exception as e:
        print(f"  Warning: Failed to fetch Intel list: {e}")

    # Fetch AMD
    try:
        html = fetch_page(AMD_URL)
        amd_cpus = extract_cpu_names_from_table(html)
        if len(amd_cpus) < 10:
            amd_cpus += extract_cpu_names_from_lists(html)
        amd_cpus = normalize_amd_entries(amd_cpus)
        print(f"  Found {len(amd_cpus)} AMD entries")
    except Exception as e:
        print(f"  Warning: Failed to fetch AMD list: {e}")

    # Fetch Qualcomm
    try:
        html = fetch_page(QUALCOMM_URL)
        qualcomm_cpus = extract_cpu_names_from_table(html)
        if len(qualcomm_cpus) < 5:
            qualcomm_cpus += extract_cpu_names_from_lists(html)
        qualcomm_cpus = list(set(e.strip() for e in qualcomm_cpus if e.strip()))
        print(f"  Found {len(qualcomm_cpus)} Qualcomm entries")
    except Exception as e:
        print(f"  Warning: Failed to fetch Qualcomm list: {e}")

    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)

    data = {
        "metadata": {
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "Microsoft Learn - Windows 11 24H2 supported processors",
            "intelUrl": INTEL_URL,
            "amdUrl": AMD_URL,
            "qualcommUrl": QUALCOMM_URL,
            "counts": {
                "intel": len(intel_cpus),
                "amd": len(amd_cpus),
                "qualcomm": len(qualcomm_cpus)
            }
        },
        "intel": sorted(intel_cpus),
        "amd": sorted(amd_cpus),
        "qualcomm": sorted(qualcomm_cpus)
    }

    output_path = os.path.join(output_dir, "windows11-supported-cpus.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = len(intel_cpus) + len(amd_cpus) + len(qualcomm_cpus)
    print(f"Generated {output_path} with {total} total entries")


if __name__ == "__main__":
    main()
