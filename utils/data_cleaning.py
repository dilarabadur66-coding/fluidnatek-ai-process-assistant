import pandas as pd


def clean_column_names(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    return df


def remove_empty_rows(df):
    df = df.copy()
    return df.dropna(how="all")


def fill_missing_values(df, fill_value=""):
    df = df.copy()
    return df.fillna(fill_value)


def extract_first_number(value):
    if value is None:
        return None

    text = str(value).replace(",", ".")
    number = pd.Series([text]).str.extract(r"(-?\d+\.?\d*)")[0].iloc[0]

    if pd.isna(number):
        return None

    return float(number)


def clean_numeric_series(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", ".")
        .str.extract(r"(-?\d+\.?\d*)")[0],
        errors="coerce"
    )