import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st


DATABASE_PATH = Path("data/processed/unified_experiments_database.json")


# -----------------------------
# DATABASE HELPERS
# -----------------------------
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


# -----------------------------
# DROPDOWN OPTIONS
# -----------------------------
def unique_sorted(values):
    clean_values = []

    for value in values:
        if value not in ["", None, {}] and value not in clean_values:
            clean_values.append(value)

    return sorted(clean_values)


def get_project_options(records):
    return unique_sorted([
        record.get("project_code", "")
        for record in records
    ])


def get_formula_options(records):
    return unique_sorted([
        record.get("formula_id", "")
        for record in records
    ])


def get_polymer_options(records):
    polymers = []

    for record in records:
        composition = record.get("solution_composition", {})
        polymer = composition.get("polymer_a", "")

        if polymer:
            polymers.append(polymer)

    return unique_sorted(polymers)


def get_solvent_options(records):
    solvents = []

    for record in records:
        composition = record.get("solution_composition", {})
        solvent = composition.get("solvent_a", "")

        if solvent:
            solvents.append(solvent)

    return unique_sorted(solvents)


def get_machine_options(records):
    return unique_sorted([
        record.get("setup", {}).get("machine", "")
        for record in records
    ])


# -----------------------------
# EXPERIMENT HELPERS
# -----------------------------
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
        "solvent": composition.get("solvent_a", ""),
        "machine": setup.get("machine", ""),
        "Q1 (mL/h)": process.get("flow_rate_q1_ml_h", ""),
        "HV+ (kV)": process.get("hv_positive_kv", ""),
        "HV- (kV)": process.get("hv_negative_kv", ""),
        "T (°C)": process.get("temperature_c", ""),
        "RH (%)": process.get("relative_humidity_percent", ""),
        "Position Y": process.get("position_y", ""),
        "dZ (mm)": process.get("dz_mm", ""),
        "grade": results.get("processability_grade", ""),
        "fiber_diameter_nm": results.get("avg_fiber_diameter_nm", ""),
        "comments": results.get("process_comments", ""),
    }


def similarity_score(exp, query):
    score = 0
    max_score = 0

    process = exp.get("process_parameters", {})
    setup = exp.get("setup", {})
    composition = exp.get("solution_composition", {})

    max_score += 25
    material_text = str(composition.get("polymer_a", "")).lower()
    query_material = str(query.get("material", "")).lower()

    if query_material and (
        query_material in material_text or material_text in query_material
    ):
        score += 25

    max_score += 15
    solvent_text = str(composition.get("solvent_a", "")).lower()
    query_solvent = str(query.get("solvent", "")).lower()

    if query_solvent and (
        query_solvent in solvent_text or solvent_text in query_solvent
    ):
        score += 15

    max_score += 10
    machine_text = str(setup.get("machine", "")).lower()
    query_machine = str(query.get("machine", "")).lower()

    if query_machine and (
        query_machine in machine_text or machine_text in query_machine
    ):
        score += 10

    numeric_fields = [
        ("flow_rate_q1_ml_h", "flow", 15, 0.5),
        ("hv_positive_kv", "hv_plus", 15, 2.0),
        ("hv_negative_kv", "hv_minus", 5, 2.0),
        ("temperature_c", "temperature", 5, 5.0),
        ("relative_humidity_percent", "humidity", 5, 10.0),
        ("position_y", "position_y", 10, 20.0),
        ("dz_mm", "dz", 10, 20.0),
    ]

    for exp_key, query_key, weight, tolerance in numeric_fields:
        max_score += weight

        exp_value = to_float(process.get(exp_key, ""))
        query_value = to_float(query.get(query_key, ""))

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


def search_similar_experiments(
    records,
    query,
    minimum_similarity=50,
    maximum_results=10
):
    scored = []

    for exp in records:
        score = similarity_score(exp, query)

        if score >= minimum_similarity:
            scored.append((score, exp))

    scored.sort(key=lambda item: item[0], reverse=True)

    return scored[:maximum_results]
    

def calculate_numeric_summary(values):
    clean_values = [
        value
        for value in values
        if value is not None
    ]

    if not clean_values:
        return None

    return {
        "minimum": round(min(clean_values), 2),
        "maximum": round(max(clean_values), 2),
        "average": round(
            sum(clean_values) / len(clean_values),
            2
        ),
    }

def analyze_similar_experiments(similar_experiments, query):
    successful_experiments = []
    all_grades = []
    fiber_diameters = []

    parameter_values = {
        "Q1 (mL/h)": [],
        "HV+ (kV)": [],
        "HV- (kV)": [],
        "T (C)": [],
        "RH (%)": [],
        "Position Y": [],
        "dZ (mm)": [],
    }

    process_keys = {
        "Q1 (mL/h)": "flow_rate_q1_ml_h",
        "HV+ (kV)": "hv_positive_kv",
        "HV- (kV)": "hv_negative_kv",
        "T (C)": "temperature_c",
        "RH (%)": "relative_humidity_percent",
        "Position Y": "position_y",
        "dZ (mm)": "dz_mm",
    }

    comments = []

    for score, experiment in similar_experiments:
        process = experiment.get("process_parameters", {})
        results = experiment.get("results", {})

        grade = to_float(
            results.get("processability_grade", "")
        )

        fiber = to_float(
            results.get("avg_fiber_diameter_nm", "")
        )

        if grade is not None:
            all_grades.append(grade)

        if fiber is not None:
            fiber_diameters.append(fiber)

        if grade is not None and grade >= 3:
            successful_experiments.append((score, experiment))

            for label, process_key in process_keys.items():
                value = to_float(
                    process.get(process_key, "")
                )

                if value is not None:
                    parameter_values[label].append(value)

        comment = str(
            results.get("process_comments", "")
        ).strip()

        if comment and comment not in comments:
            comments.append(comment)

    successful_count = len(successful_experiments)
    total_count = len(similar_experiments)

    if all_grades:
        expected_grade = round(
            sum(all_grades) / len(all_grades),
            2
        )
    else:
        expected_grade = None

    if fiber_diameters:
        expected_fiber = round(
            sum(fiber_diameters) / len(fiber_diameters),
            2
        )
    else:
        expected_fiber = None

    process_window = {
        label: calculate_numeric_summary(values)
        for label, values in parameter_values.items()
    }

    if total_count > 0:
        success_rate = round(
            successful_count / total_count * 100,
            1
        )
    else:
        success_rate = None

    interpretation = []

    if expected_grade is not None:
        if expected_grade >= 3.5:
            interpretation.append(
                "Historical experiments indicate high expected processability."
            )
        elif expected_grade >= 3:
            interpretation.append(
                "Historical experiments indicate acceptable expected processability."
            )
        elif expected_grade >= 2:
            interpretation.append(
                "Historical results indicate moderate processability. Parameter optimization may be required."
            )
        else:
            interpretation.append(
                "Historical experiments indicate low expected processability."
            )
    else:
        interpretation.append(
            "There is not enough historical result data to estimate processability."
        )

    if expected_fiber is not None:
        interpretation.append(
            f"The expected average fiber diameter is approximately {expected_fiber} nm."
        )
    else:
        interpretation.append(
            "There is not enough historical fiber diameter data to make an estimate."
        )

    warnings = []

    successful_rh = process_window.get("RH (%)")
    successful_flow = process_window.get("Q1 (mL/h)")
    successful_voltage = process_window.get("HV+ (kV)")

    if successful_rh:
        query_rh = to_float(query.get("humidity"))

        if query_rh is not None and (
            query_rh < successful_rh["minimum"]
            or query_rh > successful_rh["maximum"]
        ):
            warnings.append(
                "The input RH value is outside the successful historical range."
            )

    if successful_flow:
        query_flow = to_float(query.get("flow"))

        if query_flow is not None and (
            query_flow < successful_flow["minimum"]
            or query_flow > successful_flow["maximum"]
        ):
            warnings.append(
                "The input Q1 value is outside the successful historical range."
            )

    if successful_voltage:
        query_voltage = to_float(query.get("hv_plus"))

        if query_voltage is not None and (
            query_voltage < successful_voltage["minimum"]
            or query_voltage > successful_voltage["maximum"]
        ):
            warnings.append(
                "The input HV+ value is outside the successful historical range."
            )

    return {
        "total_similar_experiments": total_count,
        "successful_experiments": successful_count,
        "success_rate_percent": success_rate,
        "expected_processability_grade": expected_grade,
        "expected_fiber_diameter_nm": expected_fiber,
        "interpretation": interpretation,
        "recommended_process_window": process_window,
        "warnings": warnings,
        "historical_comments": comments[:5],
    }

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

    if grades:
        estimated_grade = round(sum(grades) / len(grades), 2)
    else:
        estimated_grade = "Not enough previous grade data"

    if fiber_diameters:
        estimated_fiber = round(sum(fiber_diameters) / len(fiber_diameters), 2)
    else:
       estimated_fiber = "No fiber diameter data found in historical memory"

    return {
        "estimated_processability_grade": estimated_grade,
        "estimated_fiber_diameter_nm": estimated_fiber,
        "based_on_experiments": len(similar_experiments),
    }


def create_new_experiment(data):
    experiment_id = (
        f"{data['project_code']}_experiment_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    return {
        "experiment_id": experiment_id,
         "sample_code": data["sample_code"],
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
        },
        "process_parameters": {
            "flow_rate_q1_ml_h": data["flow"],
            "hv_positive_kv": data["hv_plus"],
            "hv_negative_kv": data["hv_minus"],
            "temperature_c": data["temperature"],
            "relative_humidity_percent": data["humidity"],
            "position_y": data["position_y"],
            "dz_mm": data["dz"],
        },
        "results": {
            "processability_grade": data["grade"],
            "process_comments": data["comments"],
            "sem_comments": data["sem_comments"],
            "avg_fiber_diameter_nm": data["fiber_diameter"],
        },
        "source": "Streamlit App",
    }

# -----------------------------
# STREAMLIT APP
# -----------------------------
st.set_page_config(
    page_title="Fluidnatek AI Process Assistant",
    layout="wide"
)

st.title("🧠 Fluidnatek AI Process Assistant")
st.caption("Search previous electrospinning experiments before saving a new one.")

records = load_database()

project_options = [
    "FTK-Example",
    "LEGACY_EXCEL",
]

formula_options = [
    "FTK-Exa_PVA_1",
    "FTK-Exa_PVA_2",
]

polymer_options = [
    "PES - Polietersulfona - ULTRASON E 6020 P",
    "AcCell - Acetato de celulosa 100kDa - Fischer",
    "PEO - 900kDa - Merck",
    "PEO - 600kDa - Polyox",
    "PEO - 7MDa - Polyox",
    "PEO - 4MDa - Alroko",
    "PEO - 2MDa - Polyox",
    "PEO - 300kDa",
    "PEO - 100kDa - SIGMA ALDRICH",
    "PEO - 4MDa - Polyox",
    "POLYVIDONE KOLLIDON 30 BASF",
    "POLYVIDONE KOLLIDON 25 BASF",
    "Cellulose acetate (acetato de celulosa), Sigma, 30 kDa",
    "Ethyl Cellulose-SIGMA ALDRICH",
    "HPMC 100CP - SIGMA ALDRICH",
    "PEG - Polietilenglicol - 10kDa - Sigma Aldrich",
    "PVP 360K MERCK - SIGMA ALDRICH",
    "PCL 14000 - SIGMA ALDRICH",
    "TECOPHILIC SP-80A-150",
    "UBE NYLON 1022B",
    "TECOPHILIC HP-60D-60",
    "PEG - Polietilenglicol - 20kDa - Sigma Aldrich",
    "RESOMER RG 503 H",
    "EUDRAGIT FS 100",
    "ZEINA",
    "GELATIN NEOMODULUS",
    "CHITOSAN FOOD GRADE",
    "ALGINATE BR-L LOW VISCOSITY",
    "CELLULOSE CAB (EASTMAN)",
    "POLYACRYLONITRILE NUS",
    "PEO - 300kDa - POLYOX",
    "PVDF2821",
    "PEOR400X-ALROKO",
    "NYLON 6,6 - SIGMA ALDRICH",
    "PA 6 SP 25 KDA",
    "PVA PARTECK - EMPROVE ESSENTIAL",
    "CARBOTHANE PC 3572D",
    "TECOPHILIC HP-60D-35",
    "POLYACRYLONITRILE POWDER",
    "PEO - Xel01",
    "XP-034 - Xel01",
    "tecophilic SP-93A-100",
    "ELASTOLLAN 1195A TPU BASF"
]

solvent_options = [
    "Agua destilada",
    "Acetona",
    "Etanol",
    "DMSO - Dimetilsulfóxido - Merck",
    "DCM - Diclorometano - Merck",
    "DMC - Carbonato de dimetilo - Merck",
    "EtOAc - Acetato de etilo - Merck",
    "Ethyl Acetate (acetato de etilo) Sigma ACS reagent 99.5%",
    "DMSO - Dimetilsulfóxido - ACS reagent - Merck",
    "MeOH - Metanol - 99.6% - Sigma Aldrich",
    "formic acid 98%",
    "acetic acid - sigma-aldrich",
    "Decane",
    "Dodecane",
    "Heptane",
    "Hexadecane",
    "Mineral Oil",
    "Octane",
    "Tetradecane",
    "DMAc - Dimetilacetamida - Stockmeier Química"
]

machine_options = [
    "LE100",
    "LE500",
]
platform_options = [
    "rotacional",
]

setup_options = [
    "1",
]

if not project_options:
    project_options = ["FTK-Example"]

if not formula_options:
    formula_options = [""]

if not polymer_options:
    polymer_options = ["PEO"]

if not solvent_options:
    solvent_options = ["Agua destilada"]

if not machine_options:
    machine_options = ["le100"]

if not platform_options:
    platform_options = ["rotacional"]

if not setup_options:
    setup_options = ["1"]

st.metric("Stored Unified Experiments", len(records))

st.write("---")

# -----------------------------
# SEARCH + DECISION SECTION
# -----------------------------
st.header("1️⃣ Enter Experiment Parameters")

with st.form("search_form"):
    st.subheader("Select formulation and setup")

    col1, col2, col3 = st.columns(3)

    with col1:
        project_code = st.selectbox("Project Code", project_options)
        formula_id = st.selectbox("Formula ID", formula_options)

    with col2:
        material = st.selectbox("Polymer / Material", polymer_options)
        solvent = st.selectbox("Solvent", solvent_options)

    with col3:
        machine = st.selectbox("Machine", machine_options)

    st.subheader("Enter critical process parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        flow = st.number_input("Q1 (mL/h)", value=1.0, step=0.1)
        hv_plus = st.number_input("HV+ (kV)", value=15.0, step=0.1)

    with col2:
        hv_minus = st.number_input("HV- (kV)", value=0.0, step=0.1)
        temperature = st.number_input("T (°C)", value=25.0, step=0.1)

    with col3:
        humidity = st.number_input("RH (%)", value=40.0, step=0.1)
        position_y = st.number_input("Position Y", value=0.0, step=1.0)
        dz = st.number_input("dZ (mm)", value=150.0, step=1.0)

    submitted = st.form_submit_button("🔍 Search Memory")

query = {
    "project_code": project_code,
    "formula_id": formula_id,
    "material": material,
    "solvent": solvent,
    "machine": machine,
    "flow": flow,
    "hv_plus": hv_plus,
    "hv_minus": hv_minus,
    "temperature": temperature,
    "humidity": humidity,
    "position_y": position_y,
    "dz": dz,
}

if submitted:
    similar = search_similar_experiments(records, query)

    st.session_state["last_query"] = query
    st.session_state["similar_results"] = similar

similar = st.session_state.get(
    "similar_results",
    []
)

if similar:
    st.success(
        f"{len(similar)} relevant historical experiment(s) found."
    )

    analysis = analyze_similar_experiments(
        similar,
        query
    )

    st.subheader("AI Process Interpretation")

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Relevant Experiments",
            analysis["total_similar_experiments"]
        )

    with metric2:
        st.metric(
            "Successful Experiments",
            analysis["successful_experiments"]
        )

    with metric3:
        success_rate = analysis["success_rate_percent"]

        st.metric(
            "Historical Success Rate",
            f"{success_rate}%"
            if success_rate is not None
            else "No data"
        )

    st.write("### Expected Result")

    expected_grade = analysis[
        "expected_processability_grade"
    ]

    expected_fiber = analysis[
        "expected_fiber_diameter_nm"
    ]

    if expected_grade is not None:
        st.write(
            f"**Expected processability grade:** "
            f"{expected_grade} / 4"
        )
    else:
        st.write(
            "**Expected processability grade:** "
            "Not enough historical data"
        )

    if expected_fiber is not None:
        st.write(
            f"**Expected fiber diameter:** "
            f"{expected_fiber} nm"
        )
    else:
        st.write(
            "**Expected fiber diameter:** "
            "No historical fiber diameter data"
        )

    st.write("### Interpretation")

    for message in analysis["interpretation"]:
        st.info(message)

    st.write("### Recommended Successful Process Window")

    window_rows = []

    for parameter, statistics in analysis[
        "recommended_process_window"
    ].items():
        if statistics is not None:
            window_rows.append({
                "Parameter": parameter,
                "Minimum": statistics["minimum"],
                "Maximum": statistics["maximum"],
                "Average": statistics["average"],
            })

    if window_rows:
        st.dataframe(
            pd.DataFrame(window_rows),
            use_container_width=True
        )
    else:
        st.warning(
            "Successful process window could not be calculated."
        )

    if analysis["warnings"]:
        st.write("### Risk Warnings")

        for warning in analysis["warnings"]:
            st.warning(warning)

    if analysis["historical_comments"]:
        st.write("### Historical Engineer Comments")

        for comment in analysis["historical_comments"]:
            st.write(f"- {comment}")

elif submitted:
    st.warning("No similar experiment found.")

st.write("---")
st.header("2️⃣ Decision")

similar_from_state = st.session_state.get("similar_results", [])
query_from_state = st.session_state.get("last_query", query)

if "show_save_form" not in st.session_state:
    st.session_state["show_save_form"] = False

col_a, col_b = st.columns(2)

with col_a:
    show_similar_clicked = st.button(
        "📊 Show Similar Experiments & Success Levels"
    )

with col_b:
    if st.button("💾 Save This as New Experiment"):
        st.session_state["show_save_form"] = True

if show_similar_clicked:
    if similar_from_state:
        rows = []

        for score, exp in similar_from_state:
            row = summarize_experiment(exp)
            row["similarity_score_%"] = score
            rows.append(row)

        st.subheader("Similar Experiments and Success Levels")
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.warning("No similar experiments available. Run Search Memory first.")

if st.session_state["show_save_form"]:
    st.subheader("Complete Result Information")

    with st.form("save_result_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            sample_code = st.text_input("Sample Code",value="")
            client = st.text_input("Client", value="Anonimo")
            operator = st.text_input("R&D Leader / Operator", value="Sin asignar")
            date = st.text_input("Date", value=datetime.now().strftime("%Y-%m-%d"))

        with col2:
            concentration = st.number_input(
                "Polymer Concentration (%)",
                value=10.0,
                step=0.1
            )
            solvent_percentage = st.number_input(
                "Solvent Percentage (%)",
                value=90.0,
                step=0.1
            )

        with col3:
            setup_number = st.selectbox("Setup Number", setup_options)
            platform = st.selectbox("Platform", platform_options)

        col1, col2, col3 = st.columns(3)

        with col1:
            viscosity = st.text_input("Viscosity (cP)", value="")
            conductivity = st.text_input("Conductivity (microS)", value="")

        with col2:
            grade = st.number_input(
                "Processability Grade",
                min_value=1,
                max_value=4,
                value=3
            )
            fiber_diameter = st.text_input("Avg Fiber Diameter (nm)", value="")

        with col3:
            comments = st.text_area("Process Comments")
            sem_comments = st.text_area("SEM Comments")

        confirm_save = st.form_submit_button("✅ Confirm Save Experiment")

    if confirm_save:
        new_data = {
            "sample_code": sample_code,
            "project_code": query_from_state["project_code"],
            "client": client,
            "operator": operator,
            "date": date,
            "formula_id": query_from_state["formula_id"],
            "material": query_from_state["material"],
            "concentration": concentration,
            "solvent": query_from_state["solvent"],
            "solvent_percentage": solvent_percentage,
            "viscosity": viscosity,
            "conductivity": conductivity,
            "setup_number": setup_number,
            "machine": query_from_state["machine"],
            "platform": platform,
            "flow": query_from_state["flow"],
            "hv_plus": query_from_state["hv_plus"],
            "hv_minus": query_from_state["hv_minus"],
            "temperature": query_from_state["temperature"],
            "humidity": query_from_state["humidity"],
            "position_y": query_from_state["position_y"],
            "dz": query_from_state["dz"],
            "grade": grade,
            "comments": comments,
            "sem_comments": sem_comments,
            "fiber_diameter": fiber_diameter,
        }

        new_experiment = create_new_experiment(new_data)
        records.append(new_experiment)
        save_database(records)

        st.success(f"New experiment saved: {new_experiment['experiment_id']}")
        st.session_state["show_save_form"] = False
        st.rerun()

st.write("---")

# -----------------------------
# MEMORY TABLE
# -----------------------------
st.header("3️⃣ Experiment Memory")

if records:
    summary_rows = [summarize_experiment(exp) for exp in records]
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)
else:
    st.info("No experiments saved yet.")