import json
from dataclasses import asdict
from pathlib import Path
from typing import Any


SECTION_A_DIR = Path("data/section_a")

PROJECTS_FILE = SECTION_A_DIR / "projects.json"
MATERIALS_FILE = SECTION_A_DIR / "materials.json"
FORMULATIONS_FILE = SECTION_A_DIR / "formulations.json"
FORMULATION_COMPONENTS_FILE = SECTION_A_DIR / "formulation_components.json"
CHARACTERIZATIONS_FILE = SECTION_A_DIR / "characterizations.json"
INJECTOR_MODELS_FILE = SECTION_A_DIR / "injector_models.json"
COLLECTOR_MODELS_FILE = SECTION_A_DIR / "collector_models.json"
SETUPS_FILE = SECTION_A_DIR / "setups.json"
RUNS_FILE = SECTION_A_DIR / "runs.json"
RESULTS_FILE = SECTION_A_DIR / "results.json"


def ensure_section_a_directory():
    SECTION_A_DIR.mkdir(parents=True, exist_ok=True)


def load_records(file_path: Path) -> list[dict]:
    ensure_section_a_directory()

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except Exception:
        return []


def save_records(
    records: list[dict],
    file_path: Path
):
    ensure_section_a_directory()

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )


def add_record(
    record: Any,
    file_path: Path,
    id_field: str
):
    records = load_records(file_path)

    if hasattr(record, "__dataclass_fields__"):
        record_dict = asdict(record)
    elif isinstance(record, dict):
        record_dict = record
    else:
        raise TypeError(
            "Record must be a dataclass instance or dictionary."
        )

    record_id = record_dict.get(id_field)

    if not record_id:
        raise ValueError(
            f"Missing required ID field: {id_field}"
        )

    for existing_record in records:
        if existing_record.get(id_field) == record_id:
            raise ValueError(
                f"Duplicate record ID: {record_id}"
            )

    records.append(record_dict)
    save_records(records, file_path)

    return record_dict


def get_record_by_id(
    record_id: str,
    file_path: Path,
    id_field: str
):
    records = load_records(file_path)

    for record in records:
        if record.get(id_field) == record_id:
            return record

    return None


def update_record(
    record_id: str,
    updates: dict,
    file_path: Path,
    id_field: str
):
    records = load_records(file_path)

    for index, record in enumerate(records):
        if record.get(id_field) == record_id:
            record.update(updates)
            records[index] = record

            save_records(records, file_path)

            return record

    return None


def delete_record(
    record_id: str,
    file_path: Path,
    id_field: str
):
    records = load_records(file_path)

    filtered_records = [
        record
        for record in records
        if record.get(id_field) != record_id
    ]

    if len(filtered_records) == len(records):
        return False

    save_records(filtered_records, file_path)

    return True
# -----------------------------
# PROJECT CRUD
# -----------------------------
def add_project(project):
    return add_record(
        project,
        PROJECTS_FILE,
        "project_id"
    )


def get_project(project_id):
    return get_record_by_id(
        project_id,
        PROJECTS_FILE,
        "project_id"
    )


def update_project(project_id, updates):
    return update_record(
        project_id,
        updates,
        PROJECTS_FILE,
        "project_id"
    )


def delete_project(project_id):
    return delete_record(
        project_id,
        PROJECTS_FILE,
        "project_id"
    )


def list_projects():
    return load_records(PROJECTS_FILE)


# -----------------------------
# MATERIAL CRUD
# -----------------------------
def add_material(material):
    return add_record(
        material,
        MATERIALS_FILE,
        "material_id"
    )


def get_material(material_id):
    return get_record_by_id(
        material_id,
        MATERIALS_FILE,
        "material_id"
    )


def update_material(material_id, updates):
    return update_record(
        material_id,
        updates,
        MATERIALS_FILE,
        "material_id"
    )


def delete_material(material_id):
    return delete_record(
        material_id,
        MATERIALS_FILE,
        "material_id"
    )


def list_materials():
    return load_records(MATERIALS_FILE)


# -----------------------------
# FORMULATION CRUD
# -----------------------------
def add_formulation(formulation):
    return add_record(
        formulation,
        FORMULATIONS_FILE,
        "formulation_id"
    )


def get_formulation(formulation_id):
    return get_record_by_id(
        formulation_id,
        FORMULATIONS_FILE,
        "formulation_id"
    )


def update_formulation(formulation_id, updates):
    return update_record(
        formulation_id,
        updates,
        FORMULATIONS_FILE,
        "formulation_id"
    )


def delete_formulation(formulation_id):
    return delete_record(
        formulation_id,
        FORMULATIONS_FILE,
        "formulation_id"
    )


def list_formulations():
    return load_records(FORMULATIONS_FILE)


# -----------------------------
# FORMULATION COMPONENT CRUD
# -----------------------------
def add_formulation_component(component):
    return add_record(
        component,
        FORMULATION_COMPONENTS_FILE,
        "formulation_component_id"
    )


def list_formulation_components():
    return load_records(
        FORMULATION_COMPONENTS_FILE
    )


# -----------------------------
# CHARACTERIZATION CRUD
# -----------------------------
def add_characterization(characterization):
    return add_record(
        characterization,
        CHARACTERIZATIONS_FILE,
        "characterization_id"
    )


def list_characterizations():
    return load_records(
        CHARACTERIZATIONS_FILE
    )
# -----------------------------
# INJECTOR MODEL CRUD
# -----------------------------
def add_injector_model(injector_model):
    return add_record(
        injector_model,
        INJECTOR_MODELS_FILE,
        "injector_model_id"
    )


def get_injector_model(injector_model_id):
    return get_record_by_id(
        injector_model_id,
        INJECTOR_MODELS_FILE,
        "injector_model_id"
    )


def update_injector_model(injector_model_id, updates):
    return update_record(
        injector_model_id,
        updates,
        INJECTOR_MODELS_FILE,
        "injector_model_id"
    )


def delete_injector_model(injector_model_id):
    return delete_record(
        injector_model_id,
        INJECTOR_MODELS_FILE,
        "injector_model_id"
    )


def list_injector_models():
    return load_records(INJECTOR_MODELS_FILE)


# -----------------------------
# COLLECTOR MODEL CRUD
# -----------------------------
def add_collector_model(collector_model):
    return add_record(
        collector_model,
        COLLECTOR_MODELS_FILE,
        "collector_model_id"
    )


def get_collector_model(collector_model_id):
    return get_record_by_id(
        collector_model_id,
        COLLECTOR_MODELS_FILE,
        "collector_model_id"
    )


def update_collector_model(collector_model_id, updates):
    return update_record(
        collector_model_id,
        updates,
        COLLECTOR_MODELS_FILE,
        "collector_model_id"
    )


def delete_collector_model(collector_model_id):
    return delete_record(
        collector_model_id,
        COLLECTOR_MODELS_FILE,
        "collector_model_id"
    )


def list_collector_models():
    return load_records(COLLECTOR_MODELS_FILE)


# -----------------------------
# SETUP CRUD
# -----------------------------
def add_setup(setup):
    return add_record(
        setup,
        SETUPS_FILE,
        "setup_id"
    )


def get_setup(setup_id):
    return get_record_by_id(
        setup_id,
        SETUPS_FILE,
        "setup_id"
    )


def update_setup(setup_id, updates):
    return update_record(
        setup_id,
        updates,
        SETUPS_FILE,
        "setup_id"
    )


def delete_setup(setup_id):
    return delete_record(
        setup_id,
        SETUPS_FILE,
        "setup_id"
    )


def list_setups():
    return load_records(SETUPS_FILE)
# -----------------------------
# RUN CRUD
# -----------------------------
def add_run(run):
    return add_record(
        run,
        RUNS_FILE,
        "run_id"
    )


def get_run(run_id):
    return get_record_by_id(
        run_id,
        RUNS_FILE,
        "run_id"
    )


def update_run(run_id, updates):
    return update_record(
        run_id,
        updates,
        RUNS_FILE,
        "run_id"
    )


def delete_run(run_id):
    return delete_record(
        run_id,
        RUNS_FILE,
        "run_id"
    )


def list_runs():
    return load_records(RUNS_FILE)


# -----------------------------
# RESULT CRUD
# -----------------------------
def add_result(result):
    return add_record(
        result,
        RESULTS_FILE,
        "result_id"
    )


def get_result(result_id):
    return get_record_by_id(
        result_id,
        RESULTS_FILE,
        "result_id"
    )


def update_result(result_id, updates):
    return update_record(
        result_id,
        updates,
        RESULTS_FILE,
        "result_id"
    )


def delete_result(result_id):
    return delete_record(
        result_id,
        RESULTS_FILE,
        "result_id"
    )


def list_results():
    return load_records(RESULTS_FILE)