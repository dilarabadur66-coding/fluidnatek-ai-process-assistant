import json
import os
import pandas as pd
from datetime import datetime

MEMORY_FILE = "machine_memory.json"


# ==========================
# LOAD MEMORY
# ==========================
def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ==========================
# SAVE MEMORY
# ==========================
def save_memory(memory):

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            memory,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )


# ==========================
# ADD NEW EXPERIMENT
# ==========================
def add_experiment(
    formula,
    flow,
    voltage,
    temperature,
    grade,
    comments,
    source="Manual"
):

    memory = load_memory()

    experiment = {

        "formula": formula,
        "flow": float(flow),
        "voltage": float(voltage),
        "temperature": float(temperature),
        "grade": grade,
        "comments": comments,
        "source": source,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    }

    memory.append(experiment)

    save_memory(memory)

def search_experiment(flow=None, voltage=None, temperature=None, tolerance=0.01):

    memory = load_memory()
    matches = []

    for exp in memory:

        exp_flow = exp.get("flow", exp.get("Q1 (mL/h)", None))
        exp_voltage = exp.get("voltage", exp.get("HV+ (KV)", None))
        exp_temperature = exp.get("temperature", exp.get("T (ºC)", None))

        try:
            flow_ok = (
                flow is None
                or abs(float(exp_flow) - float(flow)) <= tolerance
            )

            voltage_ok = (
                voltage is None
                or abs(float(exp_voltage) - float(voltage)) <= tolerance
            )

            temperature_ok = (
                temperature is None
                or abs(float(exp_temperature) - float(temperature)) <= tolerance
            )

        except Exception:
            continue

        if flow_ok and voltage_ok and temperature_ok:
            matches.append(exp)

    return matches

# ==========================
# IMPORT EXCEL TO MEMORY
# ==========================
def import_excel_memory(excel_file):

    df = pd.read_excel(
        excel_file,
        sheet_name="PARÁMETROS",
        header=1
    )

    df.columns = df.columns.str.strip()
    df = df.fillna("")
    memory = []

    for _, row in df.iterrows():

        if pd.isna(row.get("Fórmula")):
            continue

        experiment = {}

        for col in df.columns:
            experiment[col] = row[col]

        memory.append(experiment)

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memory,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    return len(memory)
import re


def extract_number(value):
    if value is None:
        return None

    text = str(value).replace(",", ".")
    match = re.search(r"-?\d+\.?\d*", text)

    if not match:
        return None

    return float(match.group())


def find_similar_experiments(flow, voltage, temperature, limit=3):
    memory = load_memory()
    scored = []

    for exp in memory:
        exp_flow = extract_number(exp.get("flow", exp.get("Q1 (mL/h)", None)))
        exp_voltage = extract_number(exp.get("voltage", exp.get("HV+ (KV)", None)))
        exp_temperature = extract_number(exp.get("temperature", exp.get("T (ºC)", None)))

        if exp_flow is None or exp_voltage is None or exp_temperature is None:
            continue

        distance = (
            abs(exp_flow - float(flow)) +
            abs(exp_voltage - float(voltage)) +
            abs(exp_temperature - float(temperature))
        )

        scored.append((distance, exp))

    scored.sort(key=lambda x: x[0])

    return [exp for _, exp in scored[:limit]]