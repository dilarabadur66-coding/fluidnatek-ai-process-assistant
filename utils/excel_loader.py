from pathlib import Path

import pandas as pd


class ExcelLoader:
    """
    Reads the Excel template and returns cleaned pandas DataFrames
    for the different project sheets.
    """

    def __init__(self, excel_path):
        self.excel_path = Path(excel_path)

        if not self.excel_path.exists():
            raise FileNotFoundError(
                f"Excel file not found: {self.excel_path}"
            )

    def load_sheet(self, sheet_name, **kwargs):
        """
        Load a sheet from the Excel file.
        Extra pandas.read_excel arguments can be passed with kwargs.
        """
        return pd.read_excel(
            self.excel_path,
            sheet_name=sheet_name,
            **kwargs
        )

    @staticmethod
    def normalize_columns(df):
        """
        Remove spaces from the beginning and end of column names.

        Example:
        'FORMULA ' -> 'FORMULA'
        """
        df = df.copy()
        df.columns = [
            str(column).strip()
            for column in df.columns
        ]
        return df

    def load_materials_sheet(self):
        df = self.load_sheet("Lista_materiales")
        df = self.normalize_columns(df)

        required_columns = [
            "name",
            "category",
            "short_name",
            "polymer_family",
            "molecular_weight_kDa",
            "solvent_family",
            "available",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                "Missing columns in Lista_materiales: "
                + ", ".join(missing_columns)
            )

        df = df[required_columns].copy()
        df = df.dropna(subset=["name"])
        df = df.fillna("")
        df = df[df["name"].astype(str).str.strip() != ""]

        return df

    def load_project_details_sheet(self):
        df = self.load_sheet("Detalles_proyecto")
        df = self.normalize_columns(df)

        df = df.dropna(how="all")
        df = df.fillna("")

        return df

    def load_project_materials_sheet(self):
        df = self.load_sheet("Materiales")
        df = self.normalize_columns(df)

        material_column = (
            "Lista de materiales utilizados en el proyecto"
        )

        if material_column not in df.columns:
            raise KeyError(
                f"Missing column in Materiales: {material_column}"
            )

        df = df.dropna(subset=[material_column])
        df = df.fillna("")

        return df

    def load_solution_composition_sheet(self):
        df = self.load_sheet("Soluciones_composicion")
        df = self.normalize_columns(df)

        if "FORMULA" not in df.columns:
            raise KeyError(
                "Missing column in Soluciones_composicion: FORMULA"
            )

        df = df.dropna(subset=["FORMULA"])
        df = df.fillna("")
        df = df[
            df["FORMULA"].astype(str).str.strip() != ""
        ]

        return df

    def load_solution_properties_sheet(self):
        df = self.load_sheet("Soluciones_propiedades")
        df = self.normalize_columns(df)

        if "FORMULA" not in df.columns:
            raise KeyError(
                "Missing column in Soluciones_propiedades: FORMULA"
            )

        df = df.dropna(subset=["FORMULA"])
        df = df.fillna("")
        df = df[
            df["FORMULA"].astype(str).str.strip() != ""
        ]

        return df

    def load_setup_sheet(self):
        df = self.load_sheet("Setup")
        df = self.normalize_columns(df)

        df = df.dropna(how="all")
        df = df.fillna("")

        return df

    def load_process_parameters_sheet(self):
        df = self.load_sheet(
            "Parametros_proceso",
            header=1
        )
        df = self.normalize_columns(df)

        df = df.dropna(how="all")
        df = df.fillna("")

        return df