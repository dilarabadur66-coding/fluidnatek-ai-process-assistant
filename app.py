import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st


DATABASE_PATH = Path("data/processed/unified_experiments_database.json")


def load_database():
    if not DATABASE_PATH.exists():
        return []

    with open(DATABASE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_database(records):
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(DATABASE_PATH, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False, default=str)


def to_float(value):
    try:
        if value in ["", None]:
            return None
        return float(value)
    except Exception:
        return None


def get_process(exp):
    return exp.get("process_parameters", {})


def summarize_experiment(exp):
    process = exp.get("process_parameters", {})
    setup = exp.get("setup", {})
    composition = exp.get("solution_composition", {})
    results = exp.get("results", {})

    return {
        "experiment_id": exp.get("experiment_id", ""),
        "project_code": exp.get("project_code", ""),
        "formula_id": exp.get("formula_id", ""),
        "material": composition.get("polymer_a", ""),
        "machine": setup.get("machine", ""),
        "Q1": process.get("flow_rate_q1_ml_h", ""),
        "HV+": process.get("hv_positive_kv", ""),
        "HV-": process.get("hv_negative_kv", ""),
        "T": process.get("temperature_c", ""),
        "RH": process.get("relative_humidity_percent", ""),
        "dZ": process.get("dz_mm", ""),
        "grade": results.get("processability_grade", ""),
        "fiber_diameter_nm": results.get("avg_fiber_diameter_nm", ""),
        "comments": results.get("process_comments", ""),
    }


def similarity_score(exp, query):
    score = 0
    max_score = 0

    process = get_process(exp)
    setup = exp.get("setup", {})
    composition = exp.get("solution_composition", {})

    # Material match: very important
    max_score += 25
    if query["material"].lower() in str(composition.get("polymer_a", "")).lower():
        score += 25

    # Solvent match
    max_score += 15
    if query["solvent"].lower() in str(composition.get("solvent_a", "")).lower():
        score += 15

    # Machine match
    max_score += 10
    if query["machine"].lower() in str(setup.get("machine", "")).lower():
        score += 10

    weighted_numeric_fields = [
        ("flow_rate_q1_ml_h", "flow", 15, 0.5),
        ("hv_positive_kv", "hv_plus", 15, 2.0),
        ("hv_negative_kv", "hv_minus", 5, 2.0),
        ("temperature_c", "temperature", 5, 5.0),
        ("relative_humidity_percent", "humidity", 5, 10.0),
        ("dz_mm", "dz", 20, 20.0),
    ]

    for exp_key, query_key, weight, tolerance in weighted_numeric_fields:
        max_score += weight

        exp_value = to_float(process.get(exp_key, ""))
        query_value = to_float(query.get(query_key))

        if exp_value is None or query_value is None:
            continue

        difference = abs(exp_value - query_value)

        if difference == 0:
            score += weight
        elif difference <= tolerance:
            score += weight * 0.75
        elif difference <= tolerance * 2:
            score += weight * 0.4

    if max_score == 0:
        return 0

    return round((score / max_score) * 100, 2)
    score = 0
    process = get_process(exp)
    setup = exp.get("setup", {})
    composition = exp.get("solution_composition", {})

    if query["material"].lower() in str(composition.get("polymer_a", "")).lower():
        score += 3

    if query["machine"].lower() in str(setup.get("machine", "")).lower():
        score += 2

    numeric_fields = [
        ("flow_rate_q1_ml_h", "flow"),
        ("hv_positive_kv", "hv_plus"),
        ("hv_negative_kv", "hv_minus"),
        ("temperature_c", "temperature"),
        ("relative_humidity_percent", "humidity"),
        ("dz_mm", "dz"),
    ]

    for exp_key, query_key in numeric_fields:
        exp_value = to_float(process.get(exp_key, ""))
        query_value = to_float(query.get(query_key))

        if exp_value is None or query_value is None:
            continue

        difference = abs(exp_value - query_value)

        if difference == 0:
            score += 3
        elif difference <= 2:
            score += 2
        elif difference <= 5:
            score += 1

    return score


def search_similar_experiments(records, query):
    scored = []

    for exp in records:
        score = similarity_score(exp, query)

        if score > 0:
            scored.append((score, exp))

    scored.sort(key=lambda item: item[0], reverse=True)

    return scored[:5]
    scored = []

    for exp in records:
        score = similarity_score(exp, query)

        if score > 0:
            scored.append((score, exp))

    scored.sort(key=lambda item: item[0], reverse=True)

    return scored[:5]


def predict_result(similar_experiments):
    grades = []
    fiber_diameters = []

    for _, exp in similar_experiments:
        results = exp.get("results", {})

        grade = to_float(results.get("processability_grade", ""))
        fiber = to_float(results.get("avg_fiber_diameter_nm", ""))

        if grade is not None:
            grades.append(grade)

        if fiber is not None:
            fiber_diameters.append(fiber)

    prediction = {}

    if grades:
        prediction["estimated_processability_grade"] = round(sum(grades) / len(grades), 2)
    else:
        prediction["estimated_processability_grade"] = "Not enough previous result data"

    if fiber_diameters:
        prediction["estimated_fiber_diameter_nm"] = round(
            sum(fiber_diameters) / len(fiber_diameters),
            2
        )
    else:
        prediction["estimated_fiber_diameter_nm"] = "Not enough previous fiber data"

    return prediction


def create_new_experiment(data):
    experiment_id = f"{data['project_code']}_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return {
        "experiment_id": experiment_id,
        "project_code": data["project_code"],
        "project": {
            "project_code": data["project_code"],
            "client": data["client"],
            "start_date": data["date"],
            "rd_leader": data["operator"],
        },
        "materials": [
            {
                "project_code": data["project_code"],
                "material_name": data["material"],
            },
            {
                "project_code": data["project_code"],
                "material_name": data["solvent"],
            },
        ],
        "formula_id": data["formula_id"],
        "solution_composition": {
            "formula_id": data["formula_id"],
            "polymer_a": data["material"],
            "polymer_a_percentage": data["concentration"],
            "solvent_a": data["solvent"],
            "solvent_a_percentage": data["solvent_percentage"],
        },
        "solution_properties": {
            "viscosity_cP": data["viscosity"],
            "conductivity_microS": data["conductivity"],
        },
        "setup": {
            "setup_number": data["setup_number"],
            "machine": data["machine"],
            "platform": data["platform"],
            "injector": data["injector"],
            "number_of_needles": data["number_of_needles"],
            "needle_gauge": data["needle_gauge"],
            "drum_type": data["drum_type"],
        },
        "process_parameters": {
            "flow_rate_q1_ml_h": data["flow"],
            "hv_positive_kv": data["hv_plus"],
            "hv_negative_kv": data["hv_minus"],
            "temperature_c": data["temperature"],
            "relative_humidity_percent": data["humidity"],
            "dz_mm": data["dz"],
        },
        "results": {
            "processability_grade": data["grade"],
            "process_comments": data["comments"],
            "sem_comments": data["sem_comments"],
            "avg_fiber_diameter_nm": data["fiber_diameter"],
        },
    }


st.set_page_config(
    page_title="Fluidnatek AI Process Assistant",
    layout="wide"
)

st.title("🧠 Fluidnatek AI Process Assistant")
st.caption("Search memory first. If no experiment exists, save a new one.")

records = load_database()

st.metric("Stored Unified Experiments", len(records))

st.write("---")

st.header("1️⃣ Enter Process Parameters")

with st.form("search_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        project_code = st.text_input("Project Code", value="FTK-Example")
        material = st.text_input("Polymer / Material", value="PEO")
        solvent = st.text_input("Solvent", value="Agua destilada")
        formula_id = st.text_input("Formula ID", value="")

    with col2:
        machine = st.text_input("Machine", value="le100")
        flow = st.number_input("Q1 Flow Rate (mL/h)", value=1.0, step=0.1)
        hv_plus = st.number_input("HV+ (kV)", value=15.0, step=0.1)
        hv_minus = st.number_input("HV- (kV)", value=0.0, step=0.1)

    with col3:
        temperature = st.number_input("Temperature (°C)", value=25.0, step=0.1)
        humidity = st.number_input("RH (%)", value=40.0, step=0.1)
        dz = st.number_input("dZ Distance (mm)", value=150.0, step=1.0)

    submitted = st.form_submit_button("🔍 Search Memory")

query = {
    "project_code": project_code,
    "material": material,
    "solvent": solvent,
    "formula_id": formula_id,
    "machine": machine,
    "flow": flow,
    "hv_plus": hv_plus,
    "hv_minus": hv_minus,
    "temperature": temperature,
    "humidity": humidity,
    "dz": dz,
}

if submitted:
    similar = search_similar_experiments(records, query)
    st.session_state["last_query"] = query
    st.session_state["similar_results"] = similar

    if similar:
        st.success(f"Found {len(similar)} similar experiment(s).")

        prediction = predict_result(similar)

        st.subheader("🧠 Expected Result Based on Previous Experiments")
        st.json(prediction)

        rows = []

        for score, exp in similar:
            row = summarize_experiment(exp)
            row["similarity_score"] = score
            rows.append(row)

        st.subheader("Previous Similar Experiments")
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

    else:
        st.warning("No similar experiment found. You can save this as a new experiment.")

st.write("---")

st.header("2️⃣ Save New Experiment")

with st.form("new_experiment_form"):
    st.subheader("Project Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        new_project_code = st.text_input("Project Code", value=project_code)
        client = st.text_input("Client", value="Anonimo")
        operator = st.text_input("R&D Leader / Operator", value="Sin asignar")

    with col2:
        date = st.text_input("Date", value=datetime.now().strftime("%Y-%m-%d"))
        new_formula_id = st.text_input("Formula ID", value=formula_id)

    st.subheader("Material and Solution")

    col1, col2, col3 = st.columns(3)

    with col1:
        new_material = st.text_input("Polymer / Material", value=material)
        concentration = st.number_input("Polymer Concentration (%)", value=10.0, step=0.1)

    with col2:
        new_solvent = st.text_input("Solvent", value=solvent)
        solvent_percentage = st.number_input("Solvent Percentage (%)", value=90.0, step=0.1)

    with col3:
        viscosity = st.text_input("Viscosity (cP)", value="")
        conductivity = st.text_input("Conductivity (microS)", value="")

    st.subheader("Machine / Setup Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        setup_number = st.text_input("Setup Number", value="1")
        new_machine = st.text_input("Machine", value=machine)
        platform = st.text_input("Platform", value="rotacional")

    with col2:
        injector = st.text_input("Injector", value="")
        number_of_needles = st.text_input("Number of Needles", value="")
        needle_gauge = st.text_input("Needle Gauge", value="")

    with col3:
        drum_type = st.text_input("Drum Type", value="")
        fiber_diameter = st.text_input("Avg Fiber Diameter (nm)", value="")

    st.subheader("Process Parameters and Result")

    col1, col2, col3 = st.columns(3)

    with col1:
        new_flow = st.number_input("Q1 Flow Rate (mL/h)", value=flow, step=0.1)
        new_hv_plus = st.number_input("HV+ (kV)", value=hv_plus, step=0.1)
        new_hv_minus = st.number_input("HV- (kV)", value=hv_minus, step=0.1)

    with col2:
        new_temperature = st.number_input("Temperature (°C)", value=temperature, step=0.1)
        new_humidity = st.number_input("RH (%)", value=humidity, step=0.1)
        new_dz = st.number_input("dZ Distance (mm)", value=dz, step=1.0)

    with col3:
        grade = st.number_input("Processability Grade", min_value=1, max_value=4, value=3)
        comments = st.text_area("Process Comments")
        sem_comments = st.text_area("SEM Comments")

    save_clicked = st.form_submit_button("💾 Save New Experiment")

if save_clicked:
    new_data = {
        "project_code": new_project_code,
        "client": client,
        "operator": operator,
        "date": date,
        "formula_id": new_formula_id,
        "material": new_material,
        "concentration": concentration,
        "solvent": new_solvent,
        "solvent_percentage": solvent_percentage,
        "viscosity": viscosity,
        "conductivity": conductivity,
        "setup_number": setup_number,
        "machine": new_machine,
        "platform": platform,
        "injector": injector,
        "number_of_needles": number_of_needles,
        "needle_gauge": needle_gauge,
        "drum_type": drum_type,
        "flow": new_flow,
        "hv_plus": new_hv_plus,
        "hv_minus": new_hv_minus,
        "temperature": new_temperature,
        "humidity": new_humidity,
        "dz": new_dz,
        "grade": grade,
        "comments": comments,
        "sem_comments": sem_comments,
        "fiber_diameter": fiber_diameter,
    }

    new_experiment = create_new_experiment(new_data)
    records.append(new_experiment)
    save_database(records)

    st.success(f"New experiment saved: {new_experiment['experiment_id']}")
    st.rerun()

st.write("---")

st.header("3️⃣ Experiment Memory")

if records:
    summary_rows = [summarize_experiment(exp) for exp in records]
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)
else:
    st.info("No experiments saved yet.")