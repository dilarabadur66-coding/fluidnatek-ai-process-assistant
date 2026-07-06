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

        def load_project_materials_sheet(self):
            df = self.load_sheet("Materiales")

        df = df.dropna(
            subset=["Lista de materiales utilizados en el proyecto"]
        )

        df = df.fillna("")

        return df

    def load_solution_composition_sheet(self):
        df = self.load_sheet("Soluciones_composicion")

        df = df.dropna(subset=["FORMULA "])
        df = df.fillna("")

        return df
    
    def load_solution_properties_sheet(self):
        df = self.load_sheet("Soluciones_propiedades")

        df = df.dropna(subset=["FORMULA "])
        df = df.fillna("")

        return df
    def load_setup_sheet(self):
        df = self.load_sheet("Setup")

        df = df.dropna(how="all")
        df = df.fillna("")
        return df
    def load_process_parameters_sheet(self):
        df = pd.read_excel(
            self.excel_path,
            sheet_name="Parametros_proceso",
            header=1
        )

        df = df.dropna(how="all")
        df = df.fillna("")

        return df