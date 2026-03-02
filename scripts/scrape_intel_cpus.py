#!/usr/bin/env python3
"""
Scrape Intel CPU data from community CSV (felixsteinke/cpu-spec-dataset).
Parses InstructionSetExtensions to compute x86-64 level and features.
"""

import csv
import io
import json
import os
import re
from datetime import datetime, timezone

import requests

CSV_URL = "https://raw.githubusercontent.com/felixsteinke/cpu-spec-dataset/main/dataset/intel-cpus.csv"

# Mapping codename -> microarchitecture for x86-64 level inference
INTEL_UARCH_LEVEL = {
    # Level 1 (basic x86-64)
    "Conroe": 1, "Merom": 1, "Penryn": 1, "Wolfdale": 1,
    "Nehalem": 1, "Westmere": 1, "Clarkdale": 1, "Arrandale": 1,
    "Gulftown": 1, "Bloomfield": 1, "Lynnfield": 1,
    "Sandy Bridge": 2, "Ivy Bridge": 2,
    # Level 2 (SSE4.2, POPCNT, CMPXCHG16B)
    "Haswell": 3, "Broadwell": 3, "Skylake": 3,
    "Kaby Lake": 3, "Coffee Lake": 3, "Whiskey Lake": 3,
    "Amber Lake": 3, "Comet Lake": 3, "Cascade Lake": 3,
    "Cannon Lake": 3, "Ice Lake": 3, "Tiger Lake": 3,
    "Rocket Lake": 3, "Cypress Cove": 3,
    # Level 3 (AVX, AVX2, BMI1/2, FMA)
    "Alder Lake": 3, "Raptor Lake": 3, "Meteor Lake": 3,
    "Arrow Lake": 3, "Lunar Lake": 3,
    # Level 4 (AVX-512) - note: consumer Alder Lake+ dropped AVX-512
    "Sapphire Rapids": 4, "Emerald Rapids": 4, "Granite Rapids": 4,
    # Atom / low-power (conservative)
    "Bonnell": 1, "Saltwell": 1, "Silvermont": 1, "Airmont": 1,
    "Goldmont": 1, "Goldmont Plus": 1, "Tremont": 2,
    "Gracemont": 3, "Crestmont": 3,
    # Xeon Phi
    "Knights Landing": 3, "Knights Mill": 3,
}

# Known Intel generation -> codename families
GEN_CODENAME = {
    1: "Nehalem", 2: "Sandy Bridge", 3: "Ivy Bridge",
    4: "Haswell", 5: "Broadwell", 6: "Skylake",
    7: "Kaby Lake", 8: "Coffee Lake", 9: "Coffee Lake",
    10: "Comet Lake", 11: "Rocket Lake", 12: "Alder Lake",
    13: "Raptor Lake", 14: "Meteor Lake",
}

FEATURE_PATTERNS = {
    "sse42": re.compile(r"SSE4\.2", re.IGNORECASE),
    "avx": re.compile(r"\bAVX\b(?!2|-)"),
    "avx2": re.compile(r"\bAVX2\b", re.IGNORECASE),
    "avx512": re.compile(r"AVX-?512", re.IGNORECASE),
    "fma": re.compile(r"\bFMA\b", re.IGNORECASE),
    "aes_ni": re.compile(r"AES|AES-NI", re.IGNORECASE),
}


def parse_generation(proc_number: str, name: str) -> int:
    """Extract Intel generation from processor number or name."""
    # Core i-series: e.g. i7-12700K -> gen 12
    m = re.search(r"i[3579]-(\d{1,2})\d{2,3}", proc_number or "")
    if m:
        return int(m.group(1))
    # Core Ultra: e.g. Ultra 7 155H -> gen 14 (Meteor Lake)
    if "Ultra" in (name or ""):
        m2 = re.search(r"Ultra\s+\d+\s+(\d)", name)
        if m2:
            first_digit = int(m2.group(1))
            if first_digit == 1:
                return 14
            elif first_digit == 2:
                return 15
    # Pentium/Celeron with 4-digit number
    m3 = re.search(r"[GN](\d)\d{3}", proc_number or "")
    if m3:
        return int(m3.group(1))
    return 0


def parse_features_from_extensions(ext_str: str) -> dict:
    """Parse InstructionSetExtensions column to feature flags."""
    features = {
        "sse42": False, "popcnt": False,
        "avx": False, "avx2": False, "avx512": False,
        "fma": False, "bmi1": False, "bmi2": False,
        "aes_ni": False, "tpm2": False
    }
    if not ext_str:
        return features

    for key, pattern in FEATURE_PATTERNS.items():
        if pattern.search(ext_str):
            features[key] = True

    # POPCNT is always present with SSE4.2 on Intel
    if features["sse42"]:
        features["popcnt"] = True

    # AVX2 implies AVX (AVX2 is a superset)
    if features["avx2"]:
        features["avx"] = True

    # On Intel, AVX2 was introduced with Haswell which also added FMA, BMI1/2, AES-NI
    if features["avx2"]:
        features["fma"] = True
        features["bmi1"] = True
        features["bmi2"] = True
        features["aes_ni"] = True

    # AVX-512 implies AVX2 chain
    if features["avx512"]:
        features["avx"] = True
        features["avx2"] = True
        features["fma"] = True
        features["bmi1"] = True
        features["bmi2"] = True
        features["aes_ni"] = True

    return features


def infer_features_from_level(level: int) -> dict:
    """Infer features from x86-64 level when extension string is missing."""
    features = {
        "sse42": False, "popcnt": False,
        "avx": False, "avx2": False, "avx512": False,
        "fma": False, "bmi1": False, "bmi2": False,
        "aes_ni": False, "tpm2": False
    }
    if level >= 2:
        features["sse42"] = True
        features["popcnt"] = True
    if level >= 3:
        features["avx"] = True
        features["avx2"] = True
        features["fma"] = True
        features["bmi1"] = True
        features["bmi2"] = True
        features["aes_ni"] = True
    if level >= 4:
        features["avx512"] = True
    return features


def compute_x86_64_level(features: dict) -> int:
    """Compute x86-64 microarchitecture level from features."""
    if features.get("avx512"):
        return 4
    if all(features.get(f) for f in ["avx", "avx2", "fma", "bmi1", "bmi2"]):
        return 3
    if features.get("sse42") and features.get("popcnt"):
        return 2
    return 1


def infer_tpm2(generation: int) -> bool:
    """Intel 8th gen+ supports PTT (firmware TPM 2.0)."""
    return generation >= 8


def parse_segment(vertical: str) -> str:
    """Normalize segment name."""
    v = (vertical or "").lower()
    if "desktop" in v:
        return "Desktop"
    if "mobile" in v or "laptop" in v:
        return "Mobile"
    if "server" in v or "workstation" in v:
        return "Server"
    if "embedded" in v:
        return "Embedded"
    return "Other"


def parse_float(val: str) -> float:
    """Safely parse a float from string."""
    if not val:
        return 0.0
    try:
        return float(re.sub(r"[^\d.]", "", val))
    except (ValueError, TypeError):
        return 0.0


def parse_int(val: str) -> int:
    """Safely parse an int from string."""
    if not val:
        return 0
    try:
        return int(re.sub(r"[^\d]", "", val))
    except (ValueError, TypeError):
        return 0


def make_id(name: str) -> str:
    """Create a slug ID from CPU name."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug


def download_csv() -> str:
    """Download the Intel CPU spec CSV."""
    print(f"Downloading Intel CPU data from {CSV_URL}...")
    resp = requests.get(CSV_URL, timeout=60)
    resp.raise_for_status()
    return resp.text


def find_codename(row: dict) -> str:
    """Try to extract codename from CSV row."""
    for key in ["CodeNameText", "CodeName", "Codename", "codename", "Code Name"]:
        if key in row and row[key]:
            val = row[key].strip()
            # Clean up "Products formerly X" format
            if val.startswith("Products formerly"):
                val = val.replace("Products formerly", "").strip()
            return val
    return ""


def infer_level_from_codename(codename: str) -> int:
    """Try to match codename to known microarchitecture level."""
    for uarch, level in INTEL_UARCH_LEVEL.items():
        if uarch.lower() in codename.lower():
            return level
    return 0


def process_csv(csv_text: str) -> list:
    """Process the CSV and return a list of CPU entries."""
    reader = csv.DictReader(io.StringIO(csv_text))
    cpus = []
    seen_ids = set()

    for row in reader:
        # The CSV uses "CpuName" as the main product name column
        name = row.get("CpuName", row.get("ProductName", "")).strip()
        if not name:
            continue

        # Skip non-launched / discontinued without useful data
        status = row.get("StatusCodeText", "").strip()

        proc_number = row.get("ProcessorNumber", "").strip()
        codename = find_codename(row)
        generation = parse_generation(proc_number, name)
        ext_str = row.get("InstructionSetExtensions", "").strip()

        # Parse features from extension string
        if ext_str:
            features = parse_features_from_extensions(ext_str)
            level = compute_x86_64_level(features)
        else:
            # Infer from codename/generation
            level = infer_level_from_codename(codename)
            if level == 0 and generation > 0:
                cn = GEN_CODENAME.get(generation, "")
                level = INTEL_UARCH_LEVEL.get(cn, 1)
            if level == 0:
                level = 1
            features = infer_features_from_level(level)

        # TPM
        features["tpm2"] = infer_tpm2(generation)

        cpu_id = make_id(name)
        if cpu_id in seen_ids:
            continue
        seen_ids.add(cpu_id)

        # Determine family
        family = "Other"
        name_lower = name.lower()
        if "core ultra" in name_lower:
            family = "Core Ultra"
        elif "core" in name_lower:
            family = "Core"
        elif "xeon" in name_lower:
            family = "Xeon"
        elif "pentium" in name_lower:
            family = "Pentium"
        elif "celeron" in name_lower:
            family = "Celeron"
        elif "atom" in name_lower:
            family = "Atom"

        cores = parse_int(row.get("CoreCount", "")) or parse_int(row.get("PerfCoreCount", ""))
        threads = parse_int(row.get("ThreadCount", ""))
        # Newer CPUs use PCoreBaseFreq/PCoreTurboFreq instead of ClockSpeed/ClockSpeedMax
        base_clock = parse_float(row.get("ClockSpeed", "")) or parse_float(row.get("PCoreBaseFreq", ""))
        boost_clock = parse_float(row.get("ClockSpeedMax", "")) or parse_float(row.get("PCoreTurboFreq", "")) or parse_float(row.get("TurboBoostTech2MaxFreq", ""))
        tdp = parse_float(row.get("MaxTDP", "")) or parse_float(row.get("ProcessorBasePower", ""))
        socket = row.get("SocketsSupported", "").strip()
        launch = row.get("BornOnDate", "").strip()
        vertical = row.get("MarketSegment", "").strip()

        # Normalize clock to GHz
        if base_clock > 100:
            base_clock = round(base_clock / 1000, 2)
        if boost_clock > 100:
            boost_clock = round(boost_clock / 1000, 2)

        cpus.append({
            "id": cpu_id,
            "vendor": "intel",
            "name": name,
            "processorNumber": proc_number,
            "family": family,
            "generation": generation,
            "codename": codename,
            "segment": parse_segment(vertical),
            "cores": cores,
            "threads": threads,
            "baseClock": base_clock,
            "boostClock": boost_clock,
            "tdpW": tdp,
            "socket": socket,
            "launchDate": launch,
            "x86_64_level": level,
            "features": features
        })

    return cpus


def main():
    csv_text = download_csv()
    cpus = process_csv(csv_text)

    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)

    data = {
        "metadata": {
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "felixsteinke/cpu-spec-dataset (Intel)",
            "count": len(cpus)
        },
        "cpus": cpus
    }

    output_path = os.path.join(output_dir, "cpu-intel.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Generated {output_path} with {len(cpus)} Intel CPUs")

    # Print level distribution
    levels = {}
    for cpu in cpus:
        l = cpu["x86_64_level"]
        levels[l] = levels.get(l, 0) + 1
    print("x86-64 level distribution:", dict(sorted(levels.items())))


if __name__ == "__main__":
    main()
