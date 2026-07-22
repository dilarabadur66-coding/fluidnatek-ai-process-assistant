import json
from pathlib import Path


SOURCE_DIR = Path("data/migration_full_test")
TARGET_DIR = Path("data/section_a")


FILES = {
    "projects.json": "project_id",
    "materials.json": "material_id",
    "formulations.json": "formulation_id",
    "formulation_components.json": "formulation_component_id",
    "characterizations.json": "characterization_id",
    "setups.json": "setup_id",
    "runs.json": "run_id",
    "results.json": "result_id",
}


def load_json(path):
    if not path.exists():
        return []

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected list in {path}"
        )

    return data


def merge_records(
    existing_records,
    historical_records,
    id_field
):
    merged = list(existing_records)

    existing_ids = {
        record.get(id_field)
        for record in existing_records
        if record.get(id_field)
    }

    added = 0
    skipped = 0

    for record in historical_records:
        record_id = record.get(id_field)

        if not record_id:
            raise ValueError(
                f"Missing {id_field} in record: {record}"
            )

        if record_id in existing_ids:
            skipped += 1
            continue

        merged.append(record)
        existing_ids.add(record_id)
        added += 1

    return merged, added, skipped
def preview_merge():
    print("")
    print("SECTION A HISTORICAL MERGE PREVIEW")
    print("==================================")

    total_existing = 0
    total_historical = 0
    total_added = 0
    total_skipped = 0

    for filename, id_field in FILES.items():
        source_file = SOURCE_DIR / filename
        target_file = TARGET_DIR / filename

        historical_records = load_json(
            source_file
        )

        existing_records = load_json(
            target_file
        )

        merged_records, added, skipped = (
            merge_records(
                existing_records,
                historical_records,
                id_field
            )
        )

        print("")
        print(filename)
        print(
            "  existing:",
            len(existing_records)
        )
        print(
            "  historical:",
            len(historical_records)
        )
        print(
            "  would add:",
            added
        )
        print(
            "  would skip:",
            skipped
        )
        print(
            "  final total:",
            len(merged_records)
        )

        total_existing += len(
            existing_records
        )

        total_historical += len(
            historical_records
        )

        total_added += added
        total_skipped += skipped

    print("")
    print("SUMMARY")
    print("=======")
    print(
        "Current Section A records:",
        total_existing
    )
    print(
        "Historical records:",
        total_historical
    )
    print(
        "Would add:",
        total_added
    )
    print(
        "Would skip as duplicate:",
        total_skipped
    )

    print("")
    print(
        "PREVIEW ONLY."
    )
    print(
        "No data/section_a files were modified."
    )
def apply_merge():
    print("")
    print("APPLYING HISTORICAL DATA MERGE")
    print("==============================")

    for filename, id_field in FILES.items():
        source_file = SOURCE_DIR / filename
        target_file = TARGET_DIR / filename

        historical_records = load_json(
            source_file
        )

        existing_records = load_json(
            target_file
        )

        merged_records, added, skipped = (
            merge_records(
                existing_records,
                historical_records,
                id_field
            )
        )

        with target_file.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                merged_records,
                file,
                indent=4,
                ensure_ascii=False,
                default=str
            )

        print(
            f"{filename}: "
            f"added={added}, "
            f"skipped={skipped}, "
            f"final={len(merged_records)}"
        )

    print("")
    print("MERGE COMPLETE")

if __name__ == "__main__":
    preview_merge()

    confirmation = input(
        "\nType APPLY to write historical data into data/section_a: "
    )

    if confirmation == "APPLY":
        apply_merge()
    else:
        print("Merge cancelled.")