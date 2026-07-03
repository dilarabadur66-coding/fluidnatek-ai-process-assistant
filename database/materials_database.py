import json
from pathlib import Path

from utils.excel_loader import ExcelLoader


DEFAULT_EXCEL_PATH = "data/raw/Template_optimizacion_proceso.xlsm"
DEFAULT_OUTPUT_PATH = "data/processed/materials_database.json"


def build_materials_database(
    excel_path=DEFAULT_EXCEL_PATH,
    output_path=DEFAULT_OUTPUT_PATH
):
    loader = ExcelLoader(excel_path)
    df = loader.load_materials_sheet()

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    records = df.to_dict(orient="records")

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)

    return len(records)


def load_materials_database(path=DEFAULT_OUTPUT_PATH):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def find_material_by_short_name(short_name, path=DEFAULT_OUTPUT_PATH):
    materials = load_materials_database(path)

    for material in materials:
        if str(material.get("short_name", "")).lower() == str(short_name).lower():
            return material

    return None