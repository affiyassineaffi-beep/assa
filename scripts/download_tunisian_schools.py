from __future__ import annotations

import argparse
import csv
from pathlib import Path
import tempfile
from typing import Iterable
import warnings

import requests
import urllib3
import xlrd

DATASET_PAGE = "https://catalog.data.gov.tn/fr/dataset/liste-des-coordonnees-gps-relatives-aux-etablissements-scolaires"
DATASET_ID = "9e84a521-5a90-461a-8fd9-8b30ba85bcc3"
RESOURCE_ID = "ff93e73a-1b67-4f63-bc9a-0ad4f4043789"
DOWNLOAD_URL = "https://data.gov.tn/cms/download/9e84a521-5a90-461a-8fd9-8b30ba85bcc3/ff93e73a-1b67-4f63-bc9a-0ad4f4043789/aHR0cHM6Ly9jYXRhbG9nLmRhdGEuZ292LnRuL2RhdGFzZXQvOWU4NGE1MjEtNWE5MC00NjFhLThmZDktOGIzMGJhODViY2MzL3Jlc291cmNlL2ZmOTNlNzNhLTFiNjctNGY2My1iYzlhLTBhZDRmNDA0Mzc4OS9kb3dubG9hZC9ncHNfZXRhYmxpc3NlbWVudHNfc2NvbGFpcmVzLnhscw=="

TYPE_TO_LEVEL = {
    "E.PRIMAIRE": "Primary",
    "E.PREP": "Preparatory",
    "E.PREP.TECH": "Preparatory",
    "LYCEE": "Secondary",
}

CRE_NORMALIZATION = {
    "GABES": "Gabès",
    "GAFSA": "Gafsa",
    "KEBILI": "Kébili",
    "KEF": "Kef",
    "NABEUL": "Nabeul",
    "SFAX 1": "Sfax 1",
    "TOZEUR": "Tozeur",
    "ZAGHOUAN": "Zaghouan",
    "bizerte": "Bizerte",
}


def download_xls(output_path: Path, insecure: bool) -> Path:
    if insecure:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

    response = requests.get(
        DOWNLOAD_URL,
        timeout=90,
        verify=not insecure,
        headers={"User-Agent": "Mozilla/5.0 TunisianSchoolsImporter/1.0"},
    )
    response.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)
    return output_path


def clean_text(value: object) -> str:
    text = str(value or "").strip()
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return " ".join(text.split())


def normalize_location(value: object) -> str:
    location = clean_text(value)
    return CRE_NORMALIZATION.get(location, location)


def normalize_level(value: object) -> str:
    return TYPE_TO_LEVEL.get(clean_text(value).upper(), "")


def iter_schools_from_xls(path: Path) -> Iterable[dict[str, str]]:
    workbook = xlrd.open_workbook(str(path))
    sheet = workbook.sheet_by_index(0)
    headers = [clean_text(sheet.cell_value(0, column)) for column in range(sheet.ncols)]

    name_index = headers.index("nom_etablissement")
    location_index = headers.index("CRE")
    type_index = headers.index("Type")

    seen = set()
    for row_index in range(1, sheet.nrows):
        name = clean_text(sheet.cell_value(row_index, name_index))
        location = normalize_location(sheet.cell_value(row_index, location_index))
        level = normalize_level(sheet.cell_value(row_index, type_index))

        if not name or not location or not level:
            continue

        key = (name.casefold(), location.casefold(), level.casefold())
        if key in seen:
            continue
        seen.add(key)

        yield {"name": name, "location": location, "level": level}


def write_schools_csv(schools: Iterable[dict[str, str]], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(schools, key=lambda row: (row["location"], row["level"], row["name"]))

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "location", "level"])
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and normalize official Tunisian school data.")
    parser.add_argument("--output", default="data/schools.csv", help="Destination CSV path.")
    parser.add_argument("--raw-output", default="data/gps_etablissements_scolaires.xls", help="Destination raw XLS path.")
    parser.add_argument("--input-xls", help="Use an existing XLS file instead of downloading.")
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification for catalog download if the local CA store rejects data.gov.tn.")
    args = parser.parse_args()

    output_path = Path(args.output)
    raw_path = Path(args.raw_output)

    if args.input_xls:
        source_xls = Path(args.input_xls)
    else:
        try:
            source_xls = download_xls(raw_path, insecure=args.insecure)
        except requests.exceptions.SSLError:
            if args.insecure:
                raise
            print("TLS verification failed for data.gov.tn; retrying with --insecure mode.")
            source_xls = download_xls(raw_path, insecure=True)

    count = write_schools_csv(iter_schools_from_xls(source_xls), output_path)
    print(f"Wrote {count} schools to {output_path}")
    print(f"Source dataset: {DATASET_PAGE}")


if __name__ == "__main__":
    main()
