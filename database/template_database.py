import json
from pathlib import Path

from utils.excel_loader import ExcelLoader


DEFAULT_EXCEL_PATH = "data/raw/8_POCS_ADHESIVO_2.xlsm"
DEFAULT_PROCESSED_DIR = "data/processed/8_POCS_ADHESIVO_2"
DEFAULT_PROJECT_CODE = "8_POCS_ADHESIVO_2"


def save_json(records, output_path):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False,
            default=str,
        )


def get_value(row, *column_names, default=""):
    """
    Return the value of the first existing column.

    This allows the importer to support different versions
    of the Excel template.
    """
    for column_name in column_names:
        if column_name in row.index:
            return row[column_name]

    return default


def transform_solution_composition(
    df,
    project_code=DEFAULT_PROJECT_CODE,
):
    records = []

    for index, row in df.iterrows():
        record = {
            "composition_id": (
                f"{project_code}_composition_{index + 1}"
            ),
            "project_code": project_code,
            "formula_id": get_value(row, "FORMULA"),
            "date": get_value(row, "Fecha"),

            "solvent_a": get_value(row, "Disolvente A"),
            "solvent_a_percentage": get_value(
                row,
                "Porcentaje Disolvente A",
            ),
            "solvent_a_ratio": get_value(
                row,
                "Ratio Disolvente A",
            ),

            "solvent_b": get_value(row, "Disolvente B"),
            "solvent_b_percentage": get_value(
                row,
                "Porcentaje Disolvente B",
            ),
            "solvent_b_ratio": get_value(
                row,
                "Ratio Disolvente B",
            ),

            "solvent_c": get_value(row, "Disolvente C"),
            "solvent_c_percentage": get_value(
                row,
                "Porcentaje Disolvente C",
            ),
            "solvent_c_ratio": get_value(
                row,
                "Ratio Disolvente C",
            ),

            "polymer_a": get_value(row, "Polimero A"),
            "polymer_a_percentage": get_value(
                row,
                "Porcentaje Polimero A",
            ),
            "polymer_a_ratio": get_value(
                row,
                "Ratio Polimero A",
            ),
            "polymer_a_solids_ratio": get_value(
                row,
                "Ratio Solidos Polimero A",
            ),

            "polymer_b": get_value(row, "Polimero B"),
            "polymer_b_percentage": get_value(
                row,
                "Porcentaje Polimero B",
            ),
            "polymer_b_ratio": get_value(
                row,
                "Ratio Polimero B",
            ),
            "polymer_b_solids_ratio": get_value(
                row,
                "Ratio Solidos Polimero B",
            ),

            "polymer_c": get_value(row, "Polimero C"),
            "polymer_c_percentage": get_value(
                row,
                "Porcentaje Polimero C",
            ),
            "polymer_c_ratio": get_value(
                row,
                "Ratio Polimero C",
            ),
            "polymer_c_solids_ratio": get_value(
                row,
                "Ratio Solidos Polimero C",
            ),

            "additive_a_api": get_value(
                row,
                "Aditivo A/ API",
            ),
            "additive_a_api_percentage": get_value(
                row,
                "Porcentaje Aditivo A/ API",
            ),
            "additive_a_api_solids_ratio": get_value(
                row,
                "Ratio Solidos Aditivo A/ API",
            ),

            "additive_b_api": get_value(
                row,
                "Aditivo B /API",
            ),
            "additive_b_api_percentage": get_value(
                row,
                "Porcentaje Aditivo B /API",
            ),
            "additive_b_api_solids_ratio": get_value(
                row,
                "Ratio Solidos Aditivo B /API",
            ),

            "additive_c_api": get_value(
                row,
                "Aditivo C /API",
            ),
            "additive_c_api_percentage": get_value(
                row,
                "Porcentaje Aditivo C /API",
            ),
            "additive_c_api_solids_ratio": get_value(
                row,
                "Ratio Solidos Aditivo C /API",
            ),

            "comments": get_value(row, "Comentarios"),
        }

        records.append(record)

    return records


def build_solution_composition_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=(
        f"{DEFAULT_PROCESSED_DIR}/"
        "solution_composition_database.json"
    ),
    project_code=DEFAULT_PROJECT_CODE,
):
    loader = ExcelLoader(excel_path)
    df = loader.load_solution_composition_sheet()

    records = transform_solution_composition(
        df,
        project_code=project_code,
    )

    save_json(records, output_path)

    return len(records)


def transform_solution_properties(
    df,
    project_code=DEFAULT_PROJECT_CODE,
):
    records = []

    for index, row in df.iterrows():
        record = {
            "property_id": (
                f"{project_code}_property_{index + 1}"
            ),
            "project_code": project_code,
            "formula_id": get_value(row, "FORMULA"),
            "characterization_date": get_value(
                row,
                "Fecha Caracterización",
            ),
            "viscosity_cP": get_value(
                row,
                "Viscosidad (cP)",
            ),
            "surface_tension_mN_m": get_value(
                row,
                "Tensión superficial (mN/m)",
            ),
            "conductivity_microS": get_value(
                row,
                "Conductividad (microS)",
            ),
            "solid_content_percent": get_value(
                row,
                "Contenido en sólidos (%)",
            ),
            "density_kg_l": get_value(
                row,
                "Densidad (Kg/l)",
            ),
            "ph": get_value(row, "PH"),
            "comments": get_value(row, "Comentarios"),
        }

        records.append(record)

    return records


def build_solution_properties_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=(
        f"{DEFAULT_PROCESSED_DIR}/"
        "solution_properties_database.json"
    ),
    project_code=DEFAULT_PROJECT_CODE,
):
    loader = ExcelLoader(excel_path)
    df = loader.load_solution_properties_sheet()

    records = transform_solution_properties(
        df,
        project_code=project_code,
    )

    save_json(records, output_path)

    return len(records)


def transform_setup(
    df,
    project_code=DEFAULT_PROJECT_CODE,
):
    records = []

    for index, row in df.iterrows():
        setup_number = get_value(
            row,
            "Codigo setup",
            "Numero setup",
        )

        record = {
            "setup_id": (
                f"{project_code}_setup_{index + 1}"
            ),
            "project_code": project_code,
            "setup_number": setup_number,
            "machine": get_value(row, "Maquina"),
            "platform": get_value(row, "Plataforma"),

            "number_of_injectors": get_value(
                row,
                "Numero de inyectores",
            ),
            "distance_between_injectors": get_value(
                row,
                "Distancia entre inyectores",
            ),

            "injector": get_value(row, "Inyector"),
            "number_of_needles": get_value(
                row,
                "Numero de agujas por inyector",
                "Numero de agujas",
            ),
            "needle_gauge": get_value(
                row,
                "aguja (G)",
            ),
            "needle_distance": get_value(
                row,
                "Huecos entre agujas",
                "Distancia entre agujas",
            ),

            "deflectors": get_value(
                row,
                "Deflectores",
            ),
            "substrate": get_value(
                row,
                "Sustrato",
            ),
            "collector_type": get_value(
                row,
                "Tipo de Colector",
                "Tipo de Drum",
            ),
            "drum_size": get_value(
                row,
                "Tamaño_drum",
            ),
        }

        records.append(record)

    return records


def build_setup_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=(
        f"{DEFAULT_PROCESSED_DIR}/setup_database.json"
    ),
    project_code=DEFAULT_PROJECT_CODE,
):
    loader = ExcelLoader(excel_path)
    df = loader.load_setup_sheet()

    records = transform_setup(
        df,
        project_code=project_code,
    )

    save_json(records, output_path)

    return len(records)


def transform_process_parameters(
    df,
    project_code=DEFAULT_PROJECT_CODE,
):
    records = []

    for index, row in df.iterrows():
        record = {
            "experiment_id": (
                f"{project_code}_experiment_{index + 1}"
            ),
            "project_code": project_code,
            "sample_code": get_value(
                row,
                "Codigo muestra",
            ),
            "setup_number": get_value(
                row,
                "Setup",
            ),
            "formula_id": get_value(
                row,
                "Formula",
            ),
            "date": get_value(
                row,
                "Fecha",
            ),
            "purpose": get_value(
                row,
                "Propósito",
            ),
            "test_time_min": get_value(
                row,
                "Tiempo de prueba (min)",
            ),
            "drum_speed_rpm": get_value(
                row,
                "Velocidad drum (rpm)",
                "Velocidad_drum (rpm)",
            ),
            "r2r_cycles": get_value(
                row,
                "Numero de ciclos (R2R)",
            ),
            "r2r_speed_mm_s": get_value(
                row,
                "Velocidad_r2r (mm/s)",
            ),
            "flow_rate_q1_ml_h": get_value(
                row,
                "Q1 (mL/h)",
            ),
            "hv_positive_kv": get_value(
                row,
                "HV+ (KV)",
            ),
            "hv_negative_kv": get_value(
                row,
                "HV- (KV)",
            ),
            "temperature_c": get_value(
                row,
                "T (ºC)",
            ),
            "relative_humidity_percent": get_value(
                row,
                "RH (%)",
            ),
            "working_distance_mm": get_value(
                row,
                "working distance (mm)",
                "dZ (mm)",
            ),
            "position_z": get_value(
                row,
                "Posicion Z",
            ),
            "position_y": get_value(
                row,
                "Posicion Y",
            ),
            "sweep_y_speed_mm_s": get_value(
                row,
                "Velocidad sweep Y (mm/s)",
            ),
            "sweep_y_amplitude_mm": get_value(
                row,
                "Amplitud Sweep Y (mm)",
            ),
            "sweep_x_speed_mm_s": get_value(
                row,
                "Velocidad sweep X  (mm/s)",
                "Velocidad sweep X (mm/s)",
            ),
            "sweep_x_amplitude_mm": get_value(
                row,
                "Amplitud Sweep X (mm)",
            ),
            "processability_grade": get_value(
                row,
                "Grado de Procesabilidad",
            ),
            "process_comments": get_value(
                row,
                "Comentarios del Proceso",
            ),
            "sem_morphology": get_value(
                row,
                "Morfología SEM",
            ),
            "sem_comments": get_value(
                row,
                "Comentarios SEM",
            ),
            "avg_fiber_diameter_nm": get_value(
                row,
                "avg fiber diameter (nm)",
            ),
        }

        records.append(record)

    return records


def build_process_parameters_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=(
        f"{DEFAULT_PROCESSED_DIR}/"
        "process_parameters_database.json"
    ),
    project_code=DEFAULT_PROJECT_CODE,
):
    loader = ExcelLoader(excel_path)
    df = loader.load_process_parameters_sheet()

    records = transform_process_parameters(
        df,
        project_code=project_code,
    )

    save_json(records, output_path)

    return len(records)


def main():
    print("\nBUILDING PROCESSED DATABASES")
    print("=" * 50)

    composition_count = (
        build_solution_composition_database()
    )
    print(
        f"Solution compositions: {composition_count}"
    )

    properties_count = (
        build_solution_properties_database()
    )
    print(
        f"Solution properties: {properties_count}"
    )

    setup_count = build_setup_database()
    print(f"Setups: {setup_count}")

    process_count = (
        build_process_parameters_database()
    )
    print(
        f"Process parameters: {process_count}"
    )

    print("=" * 50)
    print(
        f"JSON files created in: "
        f"{DEFAULT_PROCESSED_DIR}"
    )


if __name__ == "__main__":
    main()