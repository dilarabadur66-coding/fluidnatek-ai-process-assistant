import json
from pathlib import Path

PROCESSED_DIR = Path("data/processed")

PROJECTS_PATH = PROCESSED_DIR / "projects_database.json"
PROJECT_MATERIALS_PATH = PROCESSED_DIR / "project_materials_database.json"
SOLUTION_COMPOSITION_PATH = PROCESSED_DIR / "solution_composition_database.json"
SOLUTION_PROPERTIES_PATH = PROCESSED_DIR / "solution_properties_database.json"
SETUP_PATH = PROCESSED_DIR / "setup_database.json"
PROCESS_PARAMETERS_PATH = PROCESSED_DIR / "process_parameters_database.json"

UNIFIED_OUTPUT_PATH = PROCESSED_DIR / "unified_experiments_database.json"


def load_json(path):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(records, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False, default=str)


def find_first_by_key(records, key, value):
    for record in records:
        if str(record.get(key, "")) == str(value):
            return record

    return {}


def build_unified_experiments_database(
    output_path=UNIFIED_OUTPUT_PATH
):
    projects = load_json(PROJECTS_PATH)
    project_materials = load_json(PROJECT_MATERIALS_PATH)
    solution_compositions = load_json(SOLUTION_COMPOSITION_PATH)
    solution_properties = load_json(SOLUTION_PROPERTIES_PATH)
    setups = load_json(SETUP_PATH)
    process_parameters = load_json(PROCESS_PARAMETERS_PATH)

    unified_records = []

    for process in process_parameters:
        project_code = process.get("project_code", "")
        formula_id = process.get("formula_id", "")
        setup_number = process.get("setup_number", "")

        project = find_first_by_key(projects, "project_code", project_code)

        materials = [
            material for material in project_materials
            if str(material.get("project_code", "")) == str(project_code)
        ]

        composition = find_first_by_key(
            solution_compositions,
            "formula_id",
            formula_id
        )

        properties = find_first_by_key(
            solution_properties,
            "formula_id",
            formula_id
        )

        setup = find_first_by_key(
            setups,
            "setup_number",
            setup_number
        )

        unified_record = {
            "experiment_id": process.get("experiment_id", ""),
            "project_code": project_code,
            "project": project,
            "materials": materials,
            "formula_id": formula_id,
            "solution_composition": composition,
            "solution_properties": properties,
            "setup": setup,
            "process_parameters": process,
            "results": {
                "processability_grade": process.get("processability_grade", ""),
                "process_comments": process.get("process_comments", ""),
                "sem_comments": process.get("sem_comments", ""),
                "avg_fiber_diameter_nm": process.get("avg_fiber_diameter_nm", ""),
            },
        }

        unified_records.append(unified_record)

    save_json(unified_records, output_path)

    return len(unified_records)


def load_unified_experiments_database(path=UNIFIED_OUTPUT_PATH):
    return load_json(path)