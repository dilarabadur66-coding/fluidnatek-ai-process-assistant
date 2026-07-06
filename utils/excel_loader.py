from pathlib import Path
import pandas as pd


class ExcelLoader:
    def __init__(self, excel_path):
        self.excel_path = Path(excel_path)

    def load_sheet(self, sheet_name):
        return pd.read_excel(
            self.excel_path,
            sheet_name=sheet_name
        )

    def load_materials_sheet(self):
        df = self.load_sheet("Lista_materiales")

        required_columns = [
            "name",
            "category",
            "short_name",
            "polymer_family",
            "molecular_weight_kDa",
            "solvent_family",
            "available"
        ]

        df = df[required_columns].copy()
        df = df.dropna(subset=["name"])
        df = df.fillna("")
        df = df[df["name"] != ""]

        return df

    def load_project_details_sheet(self):
        df = self.load_sheet("Detalles_proyecto")

        df = df.dropna(how="all")
        df = df.fillna("")

        return df