from pathlib import Path
import pandas as pd


class ExcelLoader:
    """
    Reads the reference Excel template and extracts the information
    required by the Smart Memory system.
    """

    def __init__(self, excel_path):
        self.excel_path = Path(excel_path)

    def load_sheet(self, sheet_name):
        """Load any sheet from the Excel template."""
        return pd.read_excel(
            self.excel_path,
            sheet_name=sheet_name
        )

    def load_materials_sheet(self):
        """
        Read the 'Lista_materiales' sheet and keep only
        the required columns.
        """

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

        # Remove empty rows
        df = df.dropna(subset=["name"])

        # Replace NaN values
        df = df.fillna("")

        # Remove blank names
        df = df[df["name"] != ""]

        return df


def export_materials_database(
    excel_path="data/raw/Template_optimizacion_proceso.xlsm",
    output_path="data/processed/materials_database.json"
):
    """
    Export the materials database from the Excel template
    into a JSON file.
    """

    loader = ExcelLoader(excel_path)

    df = loader.load_materials_sheet()

    df.to_json(
        output_path,
        orient="records",
        indent=4,
        force_ascii=False
    )

    print(f"✅ {len(df)} materials exported.")

    return len(df)


if __name__ == "__main__":
    export_materials_database()