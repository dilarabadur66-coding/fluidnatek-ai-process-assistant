import json
import pandas as pd
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
HISTORICAL_PROJECTS_DIR = Path("data/raw/historical_projects")


def clean_value(value):
    if pd.isna(value):
        return ""

    return value


def get_first_available(row, column_names, default=""):
    for column_name in column_names:
        if column_name in row.index:
            value = clean_value(row[column_name])

            if value not in ["", None]:
                return value

    return default


def load_formula_compositions(excel_path):
    try:
        df = pd.read_excel(
            excel_path,
            sheet_name="Soluciones_composicion"
        )

        df = df.dropna(subset=["FORMULA "], how="all")
        df = df.fillna("")

    except Exception:
        return {}

    formulas = {}

    for _, row in df.iterrows():
        formula_id = str(row.get("FORMULA ", "")).strip()

        if not formula_id:
            continue

        # Aynı formula adı birden fazla satırda bulunabilir.
        # İlk kayıt referans olarak kullanılıyor.
        if formula_id not in formulas:
            formulas[formula_id] = {
                "formula_id": formula_id,
                "date": clean_value(row.get("Fecha", "")),
                "solvent_a": clean_value(row.get("Disolvente A", "")),
                "solvent_a_percentage": clean_value(
                    row.get("Porcentaje Disolvente A", "")
                ),
                "solvent_b": clean_value(row.get("Disolvente B", "")),
                "solvent_b_percentage": clean_value(
                    row.get("Porcentaje Disolvente B", "")
                ),
                "solvent_c": clean_value(row.get("Disolvente C", "")),
                "solvent_c_percentage": clean_value(
                    row.get("Porcentaje Disolvente C", "")
                ),
                "polymer_a": clean_value(row.get("Polimero A", "")),
                "polymer_a_percentage": clean_value(
                    row.get("Porcentaje Polimero A", "")
                ),
                "polymer_b": clean_value(row.get("Polimero B", "")),
                "polymer_b_percentage": clean_value(
                    row.get("Porcentaje Polimero B", "")
                ),
                "polymer_c": clean_value(row.get("Polimero C", "")),
                "polymer_c_percentage": clean_value(
                    row.get("Porcentaje Polimero C", "")
                ),
                "comments": clean_value(row.get("Comentarios", "")),
            }

    return formulas


def load_setup_definitions(excel_path):
    try:
        df = pd.read_excel(
            excel_path,
            sheet_name="Setup"
        )

        df = df.dropna(how="all")
        df = df.fillna("")

    except Exception:
        return {}

    setups = {}

    for _, row in df.iterrows():
        setup_number = clean_value(row.get("Numero setup", ""))

        if setup_number == "":
            continue

        setups[str(setup_number)] = {
            "setup_number": setup_number,
            "machine": clean_value(row.get("Maquina", "")),
            "platform": clean_value(row.get("Plataforma", "")),
            "injector": clean_value(row.get("Inyector", "")),
            "number_of_needles": clean_value(
                row.get("Numero de agujas", "")
            ),
            "needle_gauge": clean_value(row.get("aguja (G)", "")),
            "needle_distance": clean_value(
                row.get("Distancia entre agujas", "")
            ),
            "deflectors": clean_value(row.get("Deflectores", "")),
            "substrate": clean_value(row.get("Sustrato", "")),
            "drum_type": clean_value(row.get("Tipo de Drum", "")),
            "drum_size": clean_value(row.get("Tamaño_drum", "")),
        }

    return setups


def convert_historical_excel(excel_path):
    process_df = pd.read_excel(
        excel_path,
        sheet_name="Parametros_proceso",
        header=1
    )

    process_df = process_df.dropna(how="all")
    process_df = process_df.fillna("")

    formula_compositions = load_formula_compositions(excel_path)
    setup_definitions = load_setup_definitions(excel_path)

    project_code = excel_path.stem
    converted_records = []

    for row_index, row in process_df.iterrows():
        formula_id = str(
            get_first_available(row, ["Formula", "Fórmula"])
        ).strip()

        sample_code = get_first_available(
            row,
            ["Codigo muestra", "Código muestra"]
        )

        setup_number = get_first_available(row, ["Setup"])

        # Tamamen boş placeholder satırları deney olarak alma.
        if (
            not formula_id
            and sample_code == ""
            and get_first_available(row, ["Q1 (mL/h)"]) == ""
        ):
            continue

        composition = formula_compositions.get(
            formula_id,
            {
                "formula_id": formula_id,
                "polymer_a": "",
                "solvent_a": "",
            }
        )

        setup = setup_definitions.get(
            str(setup_number),
            {
                "setup_number": setup_number,
                "machine": "",
            }
        )

        experiment_id = (
            f"historical_{excel_path.stem}_{row_index + 1}"
        )

        record = {
            "experiment_id": experiment_id,
            "project_code": project_code,
            "project": {
                "project_code": project_code,
                "client": "",
                "start_date": "",
                "rd_leader": "",
            },
            "materials": [],
            "formula_id": formula_id,
            "solution_composition": composition,
            "solution_properties": {},
            "setup": setup,
            "process_parameters": {
                "sample_code": sample_code,
                "setup_number": setup_number,
                "formula_id": formula_id,
                "date": get_first_available(row, ["Fecha"]),
                "purpose": get_first_available(row, ["Propósito"]),
                "test_time_min": get_first_available(
                    row,
                    ["Tiempo de prueba (min)"]
                ),
                "drum_speed_rpm": get_first_available(
                    row,
                    [
                        "Velocidad_drum (rpm)",
                        "Velocidad drum (rpm)",
                    ]
                ),
                "r2r_cycles": get_first_available(
                    row,
                    ["Numero de ciclos (R2R)"]
                ),
                "r2r_speed_mm_s": get_first_available(
                    row,
                    ["Velocidad_r2r (mm/s)"]
                ),
                "flow_rate_q1_ml_h": get_first_available(
                    row,
                    ["Q1 (mL/h)"]
                ),
                "hv_positive_kv": get_first_available(
                    row,
                    ["HV+ (KV)"]
                ),
                "hv_negative_kv": get_first_available(
                    row,
                    ["HV- (KV)"]
                ),
                "temperature_c": get_first_available(
                    row,
                    ["T (ºC)", "T (°C)", "T ( ºC)"]
                ),
                "relative_humidity_percent": get_first_available(
                    row,
                    ["RH (%)"]
                ),
                "position_y": get_first_available(
                    row,
                    ["Posicion Y", "Posición Y"]
                ),
                "position_z": get_first_available(
                    row,
                    ["Posicion Z", "Posición Z"]
                ),
                "dz_mm": get_first_available(
                    row,
                    [
                        "dZ (mm)",
                        "working_distance (mm)",
                        "working distance (mm)",
                    ]
                ),
                "sweep_y_speed_mm_s": get_first_available(
                    row,
                    ["Velocidad sweep Y (mm/s)"]
                ),
                "sweep_y_amplitude_mm": get_first_available(
                    row,
                    ["Amplitud Sweep Y (mm)"]
                ),
                "sweep_x_speed_mm_s": get_first_available(
                    row,
                    ["Velocidad sweep X  (mm/s)"]
                ),
                "sweep_x_amplitude_mm": get_first_available(
                    row,
                    ["Amplitud Sweep X (mm)"]
                ),
            },
            "results": {
                "processability_grade": get_first_available(
                    row,
                    ["Grado de Procesabilidad"]
                ),
                "process_comments": get_first_available(
                    row,
                    ["Comentarios del Proceso"]
                ),
                "sem_comments": get_first_available(
                    row,
                    ["Comentarios SEM", "Morfología SEM"]
                ),
                "avg_fiber_diameter_nm": get_first_available(
                    row,
                    ["avg fiber diameter (nm)"]
                ),
            },
            "source": str(excel_path),
        }

        converted_records.append(record)

    return converted_records


def import_historical_projects_to_unified(
    historical_dir=HISTORICAL_PROJECTS_DIR,
    output_path=UNIFIED_OUTPUT_PATH
):
    historical_dir = Path(historical_dir)
    unified_records = load_json(output_path)

    existing_ids = {
        record.get("experiment_id", "")
        for record in unified_records
    }

    imported_records = []
    file_results = {}

    for excel_path in sorted(historical_dir.glob("*.xlsm")):
        converted = convert_historical_excel(excel_path)

        added_for_file = 0

        for record in converted:
            if record["experiment_id"] in existing_ids:
                continue

            imported_records.append(record)
            existing_ids.add(record["experiment_id"])
            added_for_file += 1

        file_results[excel_path.name] = added_for_file

    unified_records.extend(imported_records)
    save_json(unified_records, output_path)

    return {
        "imported": len(imported_records),
        "total": len(unified_records),
        "files": file_results,
    }