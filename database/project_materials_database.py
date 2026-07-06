import json
from pathlib import Path

from utils.excel_loader import ExcelLoader

DEFAULT_EXCEL_PATH = "data/raw/Template_optimizacion_proceso.xlsm"
DEFAULT_OUTPUT_PATH = "data/processed/project_materials_database.json"


def transform_project_materials(df, project_code="FTK-Example"):
    records = []

    for _, row in df.iterrows():
        record = {
            "project_code": project_code,
            "material_number": row[" #"],
            "material_name": row["Lista de materiales utilizados en el proyecto"],
            "article_number": row["Nº de artículo"],
        }

        records.append(record)

    return records


def build_project_materials_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=DEFAULT_OUTPUT_PATH,
    project_code="FTK-Example"
):
    loader = ExcelLoader(excel_path)
    df = loader.load_project_materials_sheet()

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    records = transform_project_materials(df, project_code=project_code)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False, default=str)

    return len(records)


def load_project_materials_database(path=DEFAULT_OUTPUT_PATH):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)