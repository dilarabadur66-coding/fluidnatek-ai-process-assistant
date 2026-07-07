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
MACHINE_MEMORY_PATH = Path("machine_memory.json")


def convert_machine_memory_record(record, index):
    formula_id = record.get("formula", record.get("Fórmula", ""))
    flow = record.get("flow", record.get("Q1 (mL/h)", ""))
    voltage = record.get("voltage", record.get("HV+ (KV)", ""))
    temperature = record.get("temperature", record.get("T (ºC)", ""))
    grade = record.get("grade", record.get("Grado de Procesabilidad", ""))
    comments = record.get(
        "comments",
        record.get("Comentarios del Proceso", "")
    )

    return {
        "experiment_id": f"legacy_experiment_{index + 1}",
        "project_code": "LEGACY_EXCEL",
        "project": {
            "project_code": "LEGACY_EXCEL",
            "client": "Historical Excel Import",
            "start_date": "",
            "rd_leader": "",
        },
        "materials": [],
        "formula_id": formula_id,
        "solution_composition": {
            "formula_id": formula_id,
            "polymer_a": formula_id,
            "polymer_a_percentage": "",
            "solvent_a": "",
            "solvent_a_percentage": "",
        },
        "solution_properties": {},
        "setup": {
            "machine": "legacy setup",
        },
        "process_parameters": {
            "flow_rate_q1_ml_h": flow,
            "hv_positive_kv": voltage,
            "hv_negative_kv": "",
            "temperature_c": temperature,
            "relative_humidity_percent": "",
            "dz_mm": "",
        },
        "results": {
            "processability_grade": grade,
            "process_comments": comments,
            "sem_comments": "",
            "avg_fiber_diameter_nm": "",
        },
        "source": "machine_memory.json",
    }


def migrate_machine_memory_to_unified():
    machine_records = load_json(MACHINE_MEMORY_PATH)
    unified_records = load_json(UNIFIED_OUTPUT_PATH)

    existing_ids = {
        record.get("experiment_id", "")
        for record in unified_records
    }

    migrated_records = []

    for index, record in enumerate(machine_records):
        converted = convert_machine_memory_record(record, index)

        if converted["experiment_id"] not in existing_ids:
            migrated_records.append(converted)

    unified_records.extend(migrated_records)
    save_json(unified_records, UNIFIED_OUTPUT_PATH)

    return len(migrated_records), len(unified_records)