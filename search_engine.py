import pandas as pd
import os


def to_number(series):
    return pd.to_numeric(
        series.astype(str).str.replace(",", ".").str.strip(),
        errors="coerce"
    )


def search_previous_experiment(formula=None, flow=None, voltage=None, temperature=None):
    excel_files = [
        f for f in os.listdir(".")
        if f.lower().endswith((".xlsm", ".xlsx"))
    ]

    all_matches = []

    for file_path in excel_files:
        try:
            df = pd.read_excel(file_path, sheet_name="PARÁMETROS", header=1)
            df.columns = df.columns.str.strip()
            df = df.dropna(subset=[df.columns[0], df.columns[1]], how="all")
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            df["Fórmula"] = df["Fórmula"].ffill()

            mask = pd.Series([True] * len(df), index=df.index)

            if formula:
                formula_col = next((c for c in df.columns if "fórm" in c.lower() or "form" in c.lower()), None)
                if formula_col:
                    mask &= df[formula_col].astype(str).str.contains(str(formula), case=False, na=False)

            if flow is not None:
                flow_col = next((c for c in df.columns if "q1" in c.lower()), None)
                if flow_col:
                    mask &= (to_number(df[flow_col]) - float(flow)).abs() <= 0.01

            if voltage is not None:
                voltage_col = next((c for c in df.columns if "hv+" in c.lower() or "hv" in c.lower()), None)
                if voltage_col:
                    mask &= (to_number(df[voltage_col]) - float(voltage)).abs() <= 0.01

            if temperature is not None:
                temp_col = next((c for c in df.columns if "t (" in c.lower() or "t(" in c.lower()), None)
                if temp_col:
                    mask &= (to_number(df[temp_col]) - float(temperature)).abs() <= 0.01

            matched_results = df[mask].copy()

            if len(matched_results) > 0:
                matched_results["source_file"] = file_path
                all_matches.append(matched_results)

        except Exception:
            continue

    if all_matches:
        return pd.concat(all_matches, ignore_index=True)

    return pd.DataFrame()