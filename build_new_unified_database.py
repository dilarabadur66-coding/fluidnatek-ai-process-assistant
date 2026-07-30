import json
from pathlib import Path


PROJECT_CODE = "8_POCS_ADHESIVO_2"

SOURCE_DIR = Path(
    "data/processed/8_POCS_ADHESIVO_2"
)

OUTPUT_FILE = (
    SOURCE_DIR
    / "unified_experiments_database.json"
)


def load_json(file_path):
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a list in: {file_path}"
        )

    return data


def save_json(records, file_path):
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False,
            default=str,
        )


def normalize_text(value):
    if value is None:
        return ""

    return str(value).strip()


def build_lookup(records, key_name):
    lookup = {}

    for record in records:
        key = normalize_text(
            record.get(key_name)
        )

        if not key:
            continue

        lookup[key] = record

    return lookup

def build_formulation_components(composition):
    components = []

    component_groups = [
        ("solvent_a", "solvent"),
        ("solvent_b", "solvent"),
        ("solvent_c", "solvent"),
        ("polymer_a", "polymer"),
        ("polymer_b", "polymer"),
        ("polymer_c", "polymer"),
        ("additive_a_api", "additive"),
        ("additive_b_api", "additive"),
        ("additive_c_api", "additive"),
    ]

    formula_id = normalize_text(
        composition.get("formula_id")
    )

    for field_name, role in component_groups:
        material_name = normalize_text(
            composition.get(field_name)
        )

        if not material_name:
            continue

        component = {
            "component_id": (
                f"{formula_id}_{field_name}"
            ),
            "formula_id": formula_id,
            "material_name": material_name,
            "role": role,
            "percentage": composition.get(
                f"{field_name}_percentage",
                "",
            ),
            "ratio": composition.get(
                f"{field_name}_ratio",
                "",
            ),
            "solids_ratio": composition.get(
                f"{field_name}_solids_ratio",
                "",
            ),
        }

        components.append(component)

    return components

def build_unified_records():


    compositions = load_json(
        SOURCE_DIR
        / "solution_composition_database.json"
    )

    properties_records = load_json(
        SOURCE_DIR
        / "solution_properties_database.json"
    )

    setups = load_json(
        SOURCE_DIR
        / "setup_database.json"
    )

    process_parameters = load_json(
        SOURCE_DIR
        / "process_parameters_database.json"
    )

    composition_by_formula = build_lookup(
        compositions,
        "formula_id",
    )

    properties_by_formula = build_lookup(
        properties_records,
        "formula_id",
    )

    setup_by_number = build_lookup(
        setups,
        "setup_number",
    )

    unified_records = []

    missing_composition = 0
    missing_properties = 0
    missing_setup = 0

    for process in process_parameters:
        formula_id = normalize_text(
            process.get("formula_id")
        )

        setup_number = normalize_text(
            process.get("setup_number")
        )

        composition = composition_by_formula.get(
            formula_id,
            {},
        )

        characterization = (
            properties_by_formula.get(
                formula_id,
                {},
            )
        )

        setup = setup_by_number.get(
            setup_number,
            {},
        )

        if not composition:
            missing_composition += 1

        if not characterization:
            missing_properties += 1

        if not setup:
            missing_setup += 1

        experiment_id = normalize_text(
            process.get("experiment_id")
        )

        run_result = {
            "processability_score": (
                process.get(
                    "processability_grade",
                    "",
                )
            ),
            "process_comments": (
                process.get(
                    "process_comments",
                    "",
                )
            ),
            "sem_comments": (
                process.get(
                    "sem_comments",
                    "",
                )
            ),
            "sem_morphology": (
                process.get(
                    "sem_morphology",
                    "",
                )
            ),
            "avg_fiber_diameter_nm": (
                process.get(
                    "avg_fiber_diameter_nm",
                    "",
                )
            ),
        }

        unified_record = {
            "experiment_id": experiment_id,
            "project_code": PROJECT_CODE,
            "formula_id": formula_id,
            "project": {
                "project_code": PROJECT_CODE,
                "client": "",
                "start_date": "",
                "rd_leader": "",
            },
            "materials": [],
            "formulation": composition,
            "formulation_components": (
            build_formulation_components(
            composition
                )
            ),
            "characterization": characterization,
            "setup": setup,
            "run_parameters": process,
            "run_result": run_result,
        }

        unified_records.append(
            unified_record
        )

    summary = {
        "process_records": len(
            process_parameters
        ),
        "unified_records": len(
            unified_records
        ),
        "missing_composition": (
            missing_composition
        ),
        "missing_properties": (
            missing_properties
        ),
        "missing_setup": missing_setup,
    }

    return unified_records, summary


def main():
    print("")
    print("BUILDING NEW UNIFIED DATABASE")
    print("=" * 50)

    records, summary = (
        build_unified_records()
    )

    for key, value in summary.items():
        print(f"{key}: {value}")

    save_json(
        records,
        OUTPUT_FILE,
    )

    print("")
    print("Unified database created:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()