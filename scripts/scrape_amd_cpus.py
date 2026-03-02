#!/usr/bin/env python3
"""
Scrape AMD CPU data from community CSV (felixsteinke/cpu-spec-dataset).
Infers x86-64 level and features from microarchitecture since the CSV
lacks InstructionSetExtensions for AMD.
"""

import csv
import io
import json
import os
import re
from datetime import datetime, timezone

import requests

CSV_URL = "https://raw.githubusercontent.com/felixsteinke/cpu-spec-dataset/main/dataset/amd-cpus.csv"

# AMD microarchitecture -> x86-64 level
AMD_UARCH_LEVEL = {
    # Pre-Bulldozer (Level 1)
    "K8": 1, "K10": 1, "Bobcat": 1,
    # Bulldozer family (Level 2 - has SSE4.2, POPCNT, some AVX but no AVX2)
    "Bulldozer": 2, "Piledriver": 2, "Steamroller": 2, "Excavator": 2,
    # Jaguar/Puma (Level 1-2)
    "Jaguar": 2, "Puma": 2,
    # Zen family (Level 3 - AVX2, FMA, BMI1/2)
    "Zen": 3, "Zen+": 3, "Zen 2": 3, "Zen 3": 3,
    # Zen 4+ (Level 4 - AVX-512)
    "Zen 4": 4, "Zen 4c": 4, "Zen 5": 4,
}

# Family name patterns -> microarchitecture
# Use (?!\d) instead of \b to handle suffixes like "5800X"
AMD_FAMILY_UARCH = [
    # Ryzen - match model number (first digit = series)
    (r"Ryzen.*\s1\d{3}(?!\d)", "Zen"),        # Ryzen 1xxx -> Zen
    (r"Ryzen.*\s2\d{3}(?!\d)", "Zen+"),        # Ryzen 2xxx -> Zen+
    (r"Ryzen.*\s3\d{3}(?!\d)", "Zen 2"),       # Ryzen 3xxx -> Zen 2
    (r"Ryzen.*\s4\d{3}(?!\d)", "Zen 2"),       # Ryzen 4xxx (APU) -> Zen 2
    (r"Ryzen.*\s5\d{3}(?!\d)", "Zen 3"),       # Ryzen 5xxx -> Zen 3
    (r"Ryzen.*\s6\d{3}(?!\d)", "Zen 3"),       # Ryzen 6xxx (Mobile) -> Zen 3+
    (r"Ryzen.*\s7\d{3}(?!\d)", "Zen 4"),       # Ryzen 7xxx -> Zen 4
    (r"Ryzen.*\s8\d{3}(?!\d)", "Zen 4"),       # Ryzen 8xxx -> Zen 4
    (r"Ryzen.*\s9\d{3}(?!\d)", "Zen 5"),       # Ryzen 9xxx -> Zen 5
    # Ryzen AI 300 series
    (r"Ryzen.*AI\s+3\d{2}(?!\d)", "Zen 5"),
    # Ryzen Z series
    (r"Ryzen.*Z1", "Zen 4"),
    # EPYC
    (r"EPYC.*7[0-2]\d{2}(?!\d)", "Zen"),       # EPYC 7001 -> Zen
    (r"EPYC.*7[2-3]\d{2}(?!\d)", "Zen 2"),     # EPYC 7002 -> Zen 2
    (r"EPYC.*7[3-5]\d{2}(?!\d)", "Zen 3"),     # EPYC 7003 -> Zen 3
    (r"EPYC.*9[0-4]\d{2}(?!\d)", "Zen 4"),     # EPYC 9004 -> Zen 4
    # Threadripper
    (r"Threadripper.*1\d{3}(?!\d)", "Zen"),
    (r"Threadripper.*2\d{3}(?!\d)", "Zen+"),
    (r"Threadripper.*3\d{3}(?!\d)", "Zen 2"),
    (r"Threadripper.*5\d{3}(?!\d)", "Zen 3"),
    (r"Threadripper.*7\d{3}(?!\d)", "Zen 4"),
    # FX (Bulldozer family)
    (r"FX-\d{4}", "Piledriver"),
    # A-series APU
    (r"A[46]-\d{4}", "Steamroller"),
    (r"A[81]0?-\d{4}", "Steamroller"),
    # Athlon
    (r"Athlon.*\s2\d{2}(?!\d)", "Zen"),
    (r"Athlon.*\s3\d{3}(?!\d)", "Zen+"),
    (r"Athlon.*Gold\s+7\d{3}", "Zen 4"),
    (r"Athlon.*Silver\s+7\d{3}", "Zen 4"),
    (r"Athlon.*Gold\s+3\d{3}", "Zen"),
]


def infer_uarch_from_name(name: str) -> str:
    """Try to infer AMD microarchitecture from CPU name."""
    for pattern, uarch in AMD_FAMILY_UARCH:
        if re.search(pattern, name, re.IGNORECASE):
            return uarch
    return ""


def infer_uarch_from_codename(codename: str) -> str:
    """Try to infer AMD microarchitecture from codename field."""
    codename_lower = codename.lower()
    # Direct matches
    for uarch in ["Zen 5", "Zen 4c", "Zen 4", "Zen 3", "Zen 2", "Zen+", "Zen"]:
        if uarch.lower() in codename_lower:
            return uarch
    # Codename -> uarch mapping
    codename_map = {
        "summit ridge": "Zen", "naples": "Zen", "whitehaven": "Zen",
        "raven ridge": "Zen", "dali": "Zen",
        "pinnacle ridge": "Zen+", "colfax": "Zen+", "picasso": "Zen+",
        "matisse": "Zen 2", "rome": "Zen 2", "castle peak": "Zen 2",
        "renoir": "Zen 2", "lucienne": "Zen 2",
        "vermeer": "Zen 3", "milan": "Zen 3", "chagall": "Zen 3",
        "cezanne": "Zen 3", "barcelo": "Zen 3", "rembrandt": "Zen 3",
        "raphael": "Zen 4", "genoa": "Zen 4", "storm peak": "Zen 4",
        "phoenix": "Zen 4", "hawk point": "Zen 4",
        "granite ridge": "Zen 5", "turin": "Zen 5", "strix point": "Zen 5",
        "vishera": "Piledriver", "kaveri": "Steamroller",
        "godavari": "Steamroller", "carrizo": "Excavator",
        "bristol ridge": "Excavator",
    }
    for cn, uarch in codename_map.items():
        if cn in codename_lower:
            return uarch
    return ""


def features_from_level(level: int) -> dict:
    """Generate feature flags from x86-64 level."""
    features = {
        "sse42": False, "popcnt": False,
        "avx": False, "avx2": False, "avx512": False,
        "fma": False, "bmi1": False, "bmi2": False,
        "aes_ni": False, "tpm2": False
    }
    if level >= 2:
        features["sse42"] = True
        features["popcnt"] = True
        features["aes_ni"] = True
    if level >= 3:
        features["avx"] = True
        features["avx2"] = True
        features["fma"] = True
        features["bmi1"] = True
        features["bmi2"] = True
    if level >= 4:
        features["avx512"] = True
    return features


def infer_tpm2(uarch: str) -> bool:
    """AMD Zen+ and later support fTPM 2.0."""
    zen_with_tpm = {"Zen+", "Zen 2", "Zen 3", "Zen 4", "Zen 4c", "Zen 5"}
    # Zen 1 also supports fTPM but only on some boards; be conservative
    return uarch in zen_with_tpm or uarch == "Zen"


def parse_float(val: str) -> float:
    if not val:
        return 0.0
    try:
        return float(re.sub(r"[^\d.]", "", val))
    except (ValueError, TypeError):
        return 0.0


def parse_int(val: str) -> int:
    if not val:
        return 0
    try:
        return int(re.sub(r"[^\d]", "", val))
    except (ValueError, TypeError):
        return 0


def make_id(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug


def parse_segment(vertical: str) -> str:
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


def download_csv() -> str:
    print(f"Downloading AMD CPU data from {CSV_URL}...")
    resp = requests.get(CSV_URL, timeout=60)
    resp.raise_for_status()
    # Strip BOM if present
    text = resp.text
    if text.startswith('\ufeff'):
        text = text[1:]
    return text


def process_csv(csv_text: str) -> list:
    reader = csv.DictReader(io.StringIO(csv_text))
    cpus = []
    seen_ids = set()

    for row in reader:
        # AMD CSV uses "Model" as the primary name column
        name = row.get("Model", row.get("ProductName", "")).strip()
        if not name:
            continue

        proc_number = name  # AMD CSV doesn't have a separate processor number
        family_csv = row.get("Family", "").strip()
        codename = ""  # AMD CSV doesn't have a codename column; infer from name
        vertical = row.get("Platform", "").strip()
        launch = row.get("Launch Date", "").strip()
        process_tech = row.get("Processor Technology for CPU Cores", "").strip()

        # Determine microarchitecture from name and process tech
        uarch = infer_uarch_from_name(name)
        if not uarch and process_tech:
            # Try to infer from process technology
            if "zen 5" in process_tech.lower():
                uarch = "Zen 5"
            elif "zen 4" in process_tech.lower():
                uarch = "Zen 4"
            elif "zen 3" in process_tech.lower():
                uarch = "Zen 3"
            elif "zen 2" in process_tech.lower():
                uarch = "Zen 2"
            elif "zen+" in process_tech.lower():
                uarch = "Zen+"
            elif "zen" in process_tech.lower():
                uarch = "Zen"

        # Determine x86-64 level
        level = AMD_UARCH_LEVEL.get(uarch, 1)
        features = features_from_level(level)
        features["tpm2"] = infer_tpm2(uarch)

        cpu_id = make_id(name)
        if cpu_id in seen_ids:
            continue
        seen_ids.add(cpu_id)

        # Determine family from CSV or name
        family = "Other"
        name_lower = name.lower()
        if "ryzen" in name_lower:
            family = "Ryzen"
        elif "epyc" in name_lower:
            family = "EPYC"
        elif "threadripper" in name_lower:
            family = "Threadripper"
        elif "athlon" in name_lower:
            family = "Athlon"
        elif "fx-" in name_lower:
            family = "FX"
        elif "a4-" in name_lower or "a6-" in name_lower or "a8-" in name_lower or "a10-" in name_lower:
            family = "A-Series"
        elif family_csv:
            family = family_csv

        # Determine generation for Ryzen
        generation = 0
        m = re.search(r"Ryzen\s+\d\s+(\d)", name)
        if m:
            generation = int(m.group(1))

        cores = parse_int(row.get("# of CPU Cores", ""))
        threads = parse_int(row.get("# of Threads", ""))
        base_clock = parse_float(row.get("Base Clock", ""))
        boost_clock = parse_float(row.get("Max. Boost Clock \u00b9 \u00b2", row.get("Max. Boost Clock", "")))
        tdp = parse_float(row.get("Default TDP", ""))
        socket = row.get("CPU Socket", "").strip()

        if base_clock > 100:
            base_clock = round(base_clock / 1000, 2)
        if boost_clock > 100:
            boost_clock = round(boost_clock / 1000, 2)

        cpus.append({
            "id": cpu_id,
            "vendor": "amd",
            "name": name,
            "processorNumber": proc_number or name,
            "family": family,
            "generation": generation,
            "codename": codename,
            "microarchitecture": uarch,
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
            "source": "felixsteinke/cpu-spec-dataset (AMD)",
            "count": len(cpus)
        },
        "cpus": cpus
    }

    output_path = os.path.join(output_dir, "cpu-amd.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Generated {output_path} with {len(cpus)} AMD CPUs")

    levels = {}
    for cpu in cpus:
        l = cpu["x86_64_level"]
        levels[l] = levels.get(l, 0) + 1
    print("x86-64 level distribution:", dict(sorted(levels.items())))


if __name__ == "__main__":
    main()
