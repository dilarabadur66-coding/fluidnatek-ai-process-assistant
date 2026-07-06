import json
from pathlib import Path

from utils.excel_loader import ExcelLoader

DEFAULT_EXCEL_PATH = "data/raw/Template_optimizacion_proceso.xlsm"
DEFAULT_OUTPUT_PATH = "data/processed/projects_database.json"


def transform_project_details(df):
    project_data = {}

    for _, row in df.iterrows():
        field_name = str(row["Nombre Proyecto"]).strip()
        field_value = row["Example"]

        if field_name == "Código Proyecto":
            project_data["project_code"] = field_value
        elif field_name == "Cliente":
            project_data["client"] = field_value
        elif field_name == "Fecha de inicio":
            project_data["start_date"] = field_value
        elif field_name == "R&D Leader":
            project_data["rd_leader"] = field_value

    return [project_data]


def build_projects_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=DEFAULT_OUTPUT_PATH
):
    loader = ExcelLoader(excel_path)
    df = loader.load_project_details_sheet()

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    records = transform_project_details(df)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False, default=str)

    return len(records)


def load_projects_database(path=DEFAULT_OUTPUT_PATH):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)