import json
from pathlib import Path

from utils.excel_loader import ExcelLoader

DEFAULT_EXCEL_PATH = "data/raw/Template_optimizacion_proceso.xlsm"
DEFAULT_PROCESSED_DIR = "data/processed"


def save_json(records, output_path):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False, default=str)


def transform_solution_composition(df, project_code="FTK-Example"):
    records = []

    for index, row in df.iterrows():
        record = {
            "composition_id": f"{project_code}_composition_{index + 1}",
            "project_code": project_code,
            "formula_id": row["FORMULA "],
            "date": row["Fecha"],
            "solvent_a": row["Disolvente A"],
            "solvent_a_percentage": row["Porcentaje Disolvente A"],
            "solvent_a_ratio": row["Ratio Disolvente A"],
            "solvent_b": row["Disolvente B"],
            "solvent_b_percentage": row["Porcentaje Disolvente B"],
            "solvent_b_ratio": row["Ratio Disolvente B"],
            "solvent_c": row["Disolvente C"],
            "solvent_c_percentage": row["Porcentaje Disolvente C"],
            "solvent_c_ratio": row["Ratio Disolvente C"],
            "polymer_a": row["Polimero A"],
            "polymer_a_percentage": row["Porcentaje Polimero A"],
            "polymer_a_ratio": row["Ratio Polimero A"],
            "polymer_a_solids_ratio": row["Ratio Solidos Polimero A"],
            "polymer_b": row["Polimero B"],
            "polymer_b_percentage": row["Porcentaje Polimero B"],
            "polymer_b_ratio": row["Ratio Polimero B"],
            "polymer_b_solids_ratio": row["Ratio Solidos Polimero B"],
            "polymer_c": row["Polimero C"],
            "polymer_c_percentage": row["Porcentaje Polimero C"],
            "polymer_c_ratio": row["Ratio Polimero C"],
            "polymer_c_solids_ratio": row["Ratio Solidos Polimero C"],
            "comments": row["Comentarios"],
        }

        records.append(record)

    return records


def build_solution_composition_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=f"{DEFAULT_PROCESSED_DIR}/solution_composition_database.json",
    project_code="FTK-Example"
):
    loader = ExcelLoader(excel_path)
    df = loader.load_solution_composition_sheet()

    records = transform_solution_composition(df, project_code=project_code)
    save_json(records, output_path)

    return len(records)


def transform_solution_properties(df, project_code="FTK-Example"):
    records = []

    for index, row in df.iterrows():
        record = {
            "property_id": f"{project_code}_property_{index + 1}",
            "project_code": project_code,
            "formula_id": row["FORMULA "],
            "characterization_date": row["Fecha Caracterización"],
            "viscosity_cP": row["Viscosidad (cP)"],
            "surface_tension_mN_m": row["Tensión superficial (mN/m)"],
            "conductivity_microS": row["Conductividad (microS)"],
            "solid_content_percent": row["Contenido en sólidos (%)"],
            "density_kg_l": row["Densidad (Kg/l)"],
            "ph": row["PH"],
            "comments": row["Comentarios"],
        }

        records.append(record)

    return records


def build_solution_properties_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=f"{DEFAULT_PROCESSED_DIR}/solution_properties_database.json",
    project_code="FTK-Example"
):
    loader = ExcelLoader(excel_path)
    df = loader.load_solution_properties_sheet()

    records = transform_solution_properties(df, project_code=project_code)
    save_json(records, output_path)

    return len(records)
def transform_setup(df, project_code="FTK-Example"):
    records = []

    for index, row in df.iterrows():
        record = {
            "setup_id": f"{project_code}_setup_{index + 1}",
            "project_code": project_code,
            "setup_number": row["Numero setup"],
            "machine": row["Maquina"],
            "platform": row["Plataforma"],
            "injector": row["Inyector"],
            "number_of_needles": row["Numero de agujas"],
            "needle_gauge": row["aguja (G)"],
            "needle_distance": row["Distancia entre agujas"],
            "deflectors": row["Deflectores"],
            "substrate": row["Sustrato"],
            "drum_type": row["Tipo de Drum"],
            "drum_size": row["Tamaño_drum"],
        }

        records.append(record)

    return records
def build_setup_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=f"{DEFAULT_PROCESSED_DIR}/setup_database.json",
    project_code="FTK-Example"
):
    loader = ExcelLoader(excel_path)
    df = loader.load_setup_sheet()

    records = transform_setup(df, project_code)

    save_json(records, output_path)

    return len(records)
def transform_process_parameters(df, project_code="FTK-Example"):
    records = []

    for index, row in df.iterrows():
        record = {
            "experiment_id": f"{project_code}_experiment_{index + 1}",
            "project_code": project_code,
            "sample_code": row["Codigo muestra"],
            "setup_number": row["Setup"],
            "formula_id": row["Formula"],
            "date": row["Fecha"],
            "purpose": row["Propósito"],
            "test_time_min": row["Tiempo de prueba (min)"],
            "drum_speed_rpm": row["Velocidad_drum (rpm)"],
            "r2r_cycles": row["Numero de ciclos (R2R)"],
            "r2r_speed_mm_s": row["Velocidad_r2r (mm/s)"],
            "flow_rate_q1_ml_h": row["Q1 (mL/h)"],
            "hv_positive_kv": row["HV+ (KV)"],
            "hv_negative_kv": row["HV- (KV)"],
            "temperature_c": row["T (ºC)"],
            "relative_humidity_percent": row["RH (%)"],
            "position_y": row["Posicion Y"],
            "sweep_y_speed_mm_s": row["Velocidad sweep Y (mm/s)"],
            "sweep_y_amplitude_mm": row["Amplitud Sweep Y (mm)"],
            "dz_mm": row["dZ (mm)"],
            "sweep_x_speed_mm_s": row["Velocidad sweep X  (mm/s)"],
            "sweep_x_amplitude_mm": row["Amplitud Sweep X (mm)"],
            "processability_grade": row["Grado de Procesabilidad"],
            "process_comments": row["Comentarios del Proceso"],
            "sem_comments": row["Comentarios SEM"],
            "avg_fiber_diameter_nm": row["avg fiber diameter (nm)"],
        }

        records.append(record)

    return records


def build_process_parameters_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=f"{DEFAULT_PROCESSED_DIR}/process_parameters_database.json",
    project_code="FTK-Example"
):
    loader = ExcelLoader(excel_path)
    df = loader.load_process_parameters_sheet()

    records = transform_process_parameters(df, project_code)

    save_json(records, output_path)

    return len(records)