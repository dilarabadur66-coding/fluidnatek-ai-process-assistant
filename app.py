import re

import pandas as pd
import streamlit as st

from memory.section_a_memory_adapter import build_section_a_memory_records
from ui.projects_page import render_projects_page
from ui.materials_page import render_materials_page
from ui.formulations_page import render_formulations_page
from ui.setups_page import render_setups_page
from ui.runs_page import render_runs_page
from ui.results_page import render_results_page


st.set_page_config(
    page_title="Fluidnatek AI Process Assistant",
    layout="wide",
)


# ============================================================
# DATA
# ============================================================
def load_database():
    return build_section_a_memory_records()


# ============================================================
# BASIC HELPERS
# ============================================================
def to_float(value):
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def unique_sorted(values):
    result = []

    for value in values:
        if value in ("", None, {}):
            continue

        if value not in result:
            result.append(value)

    return sorted(
        result,
        key=lambda item: str(item).lower(),
    )


def exact_text_match(left, right):
    left = normalize_text(left)
    right = normalize_text(right)

    return bool(
        left
        and right
        and left == right
    )


def safe_text_match(left, right):
    """
    Safe partial text matching.
    Empty strings never count as matches.
    """
    left = normalize_text(left)
    right = normalize_text(right)

    if not left or not right:
        return False

    return (
        left == right
        or left in right
        or right in left
    )


def get_process(exp):
    return exp.get("process_parameters", {}) or {}


def get_setup(exp):
    return exp.get("setup", {}) or {}


def get_composition(exp):
    return exp.get("solution_composition", {}) or {}


def get_results(exp):
    return exp.get("results", {}) or {}


# ============================================================
# USER-FACING OPTION CLEANUP
# ============================================================
def is_internal_value(value):
    text = str(value or "").strip()

    if not text:
        return True

    upper = text.upper()

    return (
        upper.startswith("MIG_FORM_")
        or upper.startswith("MIG_SETUP_")
        or upper.startswith("MIG_MAT_")
        or upper.startswith("MIG_RESULT_")
        or upper.startswith("__MISSING_")
        or upper in {
            "UNKNOWN_PROJECT",
            "LEGACY_EXCEL",
            "LEGACY SETUP",
        }
    )


def clean_project_options(records):
    return unique_sorted(
        record.get("project_code", "")
        for record in records
        if not is_internal_value(
            record.get("project_code", "")
        )
    )


def clean_formula_options(records):
    return unique_sorted(
        record.get("formula_id", "")
        for record in records
        if not is_internal_value(
            record.get("formula_id", "")
        )
    )


def clean_material_options(records):
    return unique_sorted(
        get_composition(record).get("polymer_a", "")
        for record in records
        if get_composition(record).get("polymer_a", "")
    )


def clean_solvent_options(records):
    return unique_sorted(
        get_composition(record).get("solvent_a", "")
        for record in records
        if get_composition(record).get("solvent_a", "")
    )


def normalize_machine(value):
    """
    Collapse historical spelling variants into user-facing machine families.
    Example: L100, LE100, LE-100, le100 -> LE100
    """
    raw = str(value or "").strip()

    if not raw:
        return ""

    compact = re.sub(
        r"[^A-Z0-9]",
        "",
        raw.upper(),
    )

    if compact in {"L100", "LE100"}:
        return "LE100"

    if compact in {"L500", "LE500"}:
        return "LE500"

    if "LEGACY" in compact:
        return ""

    return raw


def clean_machine_options(records):
    return unique_sorted(
        normalize_machine(
            get_setup(record).get("machine", "")
        )
        for record in records
        if normalize_machine(
            get_setup(record).get("machine", "")
        )
    )


def machine_match(left, right):
    left_normalized = normalize_machine(left)
    right_normalized = normalize_machine(right)

    if not left_normalized or not right_normalized:
        return False

    return normalize_text(
        left_normalized
    ) == normalize_text(
        right_normalized
    )


def resolve_select_or_custom(
    label,
    options,
    any_label,
    custom_label,
    key_prefix,
):
    choices = [
        any_label,
        *options,
        "Other / Custom...",
    ]

    selected = st.selectbox(
        label,
        choices,
        key=f"{key_prefix}_select",
    )

    if selected == "Other / Custom...":
        custom_value = st.text_input(
            custom_label,
            key=f"{key_prefix}_custom",
            placeholder="Type a new value...",
        )
        return custom_value.strip()

    if selected == any_label:
        return ""

    return selected


# ============================================================
# EXPERIMENT SUMMARY
# ============================================================
def summarize_experiment(exp):
    process = get_process(exp)
    setup = get_setup(exp)
    composition = get_composition(exp)
    results = get_results(exp)

    return {
        "experiment_id": exp.get(
            "experiment_id",
            "",
        ),
        "project_code": exp.get(
            "project_code",
            "",
        ),
        "formula_id": (
            ""
            if is_internal_value(
                exp.get("formula_id", "")
            )
            else exp.get("formula_id", "")
        ),
        "polymer": composition.get(
            "polymer_a",
            "",
        ),
        "solvent": composition.get(
            "solvent_a",
            "",
        ),
        "machine": normalize_machine(
            setup.get("machine", "")
        ),
        "Q1 (mL/h)": process.get(
            "flow_rate_q1_ml_h",
            "",
        ),
        "HV+ (kV)": process.get(
            "hv_positive_kv",
            "",
        ),
        "HV- (kV)": process.get(
            "hv_negative_kv",
            "",
        ),
        "T (°C)": process.get(
            "temperature_c",
            "",
        ),
        "RH (%)": process.get(
            "relative_humidity_percent",
            "",
        ),
        "dZ (mm)": process.get(
            "dz_mm",
            "",
        ),
        "grade": results.get(
            "processability_grade",
            "",
        ),
        "comments": results.get(
            "process_comments",
            "",
        ),
    }


# ============================================================
# CONTEXT-AWARE GLOBAL SEARCH
# ============================================================
def context_tier(exp, query):
    """
    Search is global across Section A.

    4 = exact known formulation
    3 = same polymer + solvent
    2 = same polymer
    1 = same solvent OR fully broad/global query
    0 = incompatible with the selected scientific context
    """
    composition = get_composition(exp)

    formula_query = query.get(
        "formula_id",
        "",
    )
    polymer_query = query.get(
        "material",
        "",
    )
    solvent_query = query.get(
        "solvent",
        "",
    )

    formula_match = (
        bool(formula_query)
        and exact_text_match(
            exp.get("formula_id", ""),
            formula_query,
        )
    )

    polymer_match = (
        bool(polymer_query)
        and safe_text_match(
            composition.get("polymer_a", ""),
            polymer_query,
        )
    )

    solvent_match = (
        bool(solvent_query)
        and safe_text_match(
            composition.get("solvent_a", ""),
            solvent_query,
        )
    )

    if formula_match:
        return 4

    if polymer_match and solvent_match:
        return 3

    if polymer_match:
        return 2

    if solvent_match:
        return 1

    # Nothing scientific was specified:
    # allow a global process-parameter search.
    if not (
        formula_query
        or polymer_query
        or solvent_query
    ):
        return 1

    return 0


def similarity_score(exp, query):
    score = 0.0
    max_score = 0.0

    process = get_process(exp)
    setup = get_setup(exp)
    composition = get_composition(exp)

    context_fields = [
        (
            exp.get("formula_id", ""),
            query.get("formula_id", ""),
            35,
            exact_text_match,
        ),
        (
            composition.get("polymer_a", ""),
            query.get("material", ""),
            25,
            safe_text_match,
        ),
        (
            composition.get("solvent_a", ""),
            query.get("solvent", ""),
            15,
            safe_text_match,
        ),
        (
            setup.get("machine", ""),
            query.get("machine", ""),
            10,
            machine_match,
        ),
        (
            exp.get("project_code", ""),
            query.get("project_code", ""),
            5,
            exact_text_match,
        ),
    ]

    for (
        experiment_value,
        query_value,
        weight,
        matcher,
    ) in context_fields:
        if not normalize_text(
            query_value
        ):
            continue

        max_score += weight

        if matcher(
            experiment_value,
            query_value,
        ):
            score += weight

    numeric_fields = [
        (
            "flow_rate_q1_ml_h",
            "flow",
            15,
            0.5,
        ),
        (
            "hv_positive_kv",
            "hv_plus",
            15,
            2.0,
        ),
        (
            "hv_negative_kv",
            "hv_minus",
            5,
            2.0,
        ),
        (
            "temperature_c",
            "temperature",
            5,
            5.0,
        ),
        (
            "relative_humidity_percent",
            "humidity",
            5,
            10.0,
        ),
        (
            "dz_mm",
            "dz",
            10,
            20.0,
        ),
    ]

    for (
        exp_key,
        query_key,
        weight,
        tolerance,
    ) in numeric_fields:
        query_value = to_float(
            query.get(query_key)
        )

        if query_value is None:
            continue

        max_score += weight

        experiment_value = to_float(
            process.get(exp_key)
        )

        if experiment_value is None:
            continue

        difference = abs(
            experiment_value
            - query_value
        )

        if difference == 0:
            score += weight
        elif difference <= tolerance:
            score += weight * 0.75
        elif difference <= (
            tolerance * 2
        ):
            score += weight * 0.40

    if max_score <= 0:
        return 0.0

    return round(
        score / max_score * 100,
        2,
    )


def search_similar_experiments(
    records,
    query,
    minimum_similarity=30,
    maximum_results=12,
):
    candidates = []

    for experiment in records:
        tier = context_tier(
            experiment,
            query,
        )

        if tier == 0:
            continue

        score = similarity_score(
            experiment,
            query,
        )

        if score >= minimum_similarity:
            candidates.append(
                {
                    "tier": tier,
                    "score": score,
                    "experiment": experiment,
                }
            )

    if not candidates:
        return []

    highest_tier = max(
        candidate["tier"]
        for candidate in candidates
    )

    strongest_context = [
        candidate
        for candidate in candidates
        if candidate["tier"]
        == highest_tier
    ]

    strongest_context.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return strongest_context[
        :maximum_results
    ]


# ============================================================
# GRADE 4 ANALYSIS
# ============================================================
def calculate_numeric_summary(
    values,
):
    clean_values = [
        value
        for value in values
        if value is not None
    ]

    if not clean_values:
        return None

    return {
        "minimum": round(
            min(clean_values),
            2,
        ),
        "maximum": round(
            max(clean_values),
            2,
        ),
        "average": round(
            sum(clean_values)
            / len(clean_values),
            2,
        ),
    }


def analyze_similar_experiments(
    similar_experiments,
    query,
):
    all_grades = []
    weighted_grades = []
    grade_4_items = []
    comments = []

    parameter_values = {
        "Q1 (mL/h)": [],
        "HV+ (kV)": [],
        "HV- (kV)": [],
        "T (°C)": [],
        "RH (%)": [],
        "dZ (mm)": [],
    }

    process_keys = {
        "Q1 (mL/h)":
            "flow_rate_q1_ml_h",
        "HV+ (kV)":
            "hv_positive_kv",
        "HV- (kV)":
            "hv_negative_kv",
        "T (°C)":
            "temperature_c",
        "RH (%)":
            "relative_humidity_percent",
        "dZ (mm)":
            "dz_mm",
    }

    for item in similar_experiments:
        experiment = item[
            "experiment"
        ]
        score = item["score"]

        process = get_process(
            experiment
        )
        results = get_results(
            experiment
        )

        grade = to_float(
            results.get(
                "processability_grade"
            )
        )

        if grade is not None:
            all_grades.append(
                grade
            )
            weighted_grades.append(
                (
                    grade,
                    max(
                        score,
                        1.0,
                    ),
                )
            )

        if grade == 4:
            grade_4_items.append(
                item
            )

            for (
                label,
                process_key,
            ) in process_keys.items():
                value = to_float(
                    process.get(
                        process_key
                    )
                )

                if value is not None:
                    parameter_values[
                        label
                    ].append(
                        value
                    )

        comment = str(
            results.get(
                "process_comments",
                "",
            )
        ).strip()

        if (
            comment
            and comment not in comments
        ):
            comments.append(
                comment
            )

    graded_count = len(
        all_grades
    )
    grade_4_count = len(
        grade_4_items
    )

    if weighted_grades:
        numerator = sum(
            grade * weight
            for (
                grade,
                weight,
            ) in weighted_grades
        )
        denominator = sum(
            weight
            for (
                _,
                weight,
            ) in weighted_grades
        )

        expected_grade = round(
            numerator
            / denominator,
            2,
        )
    else:
        expected_grade = None

    grade_4_rate = (
        round(
            grade_4_count
            / graded_count
            * 100,
            1,
        )
        if graded_count
        else None
    )

    process_window = {
        label:
            calculate_numeric_summary(
                values
            )
        for (
            label,
            values,
        ) in parameter_values.items()
    }

    recommendation = {
        label:
            statistics["average"]
        for (
            label,
            statistics,
        ) in process_window.items()
        if statistics is not None
    }

    warnings = []

    query_key_map = {
        "Q1 (mL/h)": "flow",
        "HV+ (kV)": "hv_plus",
        "HV- (kV)": "hv_minus",
        "T (°C)": "temperature",
        "RH (%)": "humidity",
        "dZ (mm)": "dz",
    }

    for (
        label,
        statistics,
    ) in process_window.items():
        if not statistics:
            continue

        query_value = to_float(
            query.get(
                query_key_map[label]
            )
        )

        if query_value is None:
            continue

        if (
            query_value
            < statistics["minimum"]
            or query_value
            > statistics["maximum"]
        ):
            warnings.append(
                f"{label} is outside the "
                f"historical Grade 4 range "
                f"({statistics['minimum']} – "
                f"{statistics['maximum']})."
            )

    if expected_grade is None:
        interpretation = (
            "Not enough graded historical "
            "data for a reliable estimate."
        )
    elif expected_grade >= 3.5:
        interpretation = (
            "Historical evidence is close "
            "to the Grade 4 target."
        )
    elif expected_grade >= 3:
        interpretation = (
            "The process appears workable, "
            "but optimization is still needed "
            "to reliably reach Grade 4."
        )
    elif expected_grade >= 2:
        interpretation = (
            "Historical evidence suggests "
            "moderate processability. "
            "Parameter optimization is recommended."
        )
    else:
        interpretation = (
            "Historical evidence suggests low "
            "processability for the current conditions."
        )

    return {
        "total":
            len(similar_experiments),
        "graded":
            graded_count,
        "grade_4":
            grade_4_count,
        "grade_4_rate":
            grade_4_rate,
        "expected_grade":
            expected_grade,
        "process_window":
            process_window,
        "recommendation":
            recommendation,
        "warnings":
            warnings,
        "comments":
            comments[:5],
        "interpretation":
            interpretation,
    }


# ============================================================
# NAVIGATION
# ============================================================
page = st.sidebar.radio(
    "Navigation",
    [
        "Main App",
        "Projects",
        "Materials",
        "Formulations",
        "Setups",
        "Experimental Runs",
        "Results",
    ],
)

if page == "Projects":
    render_projects_page()
    st.stop()

if page == "Materials":
    render_materials_page()
    st.stop()

if page == "Formulations":
    render_formulations_page()
    st.stop()

if page == "Setups":
    render_setups_page()
    st.stop()

if page == "Experimental Runs":
    render_runs_page()
    st.stop()

if page == "Results":
    render_results_page()
    st.stop()


# ============================================================
# MAIN APP
# ============================================================
records = load_database()

st.title(
    "🧠 Fluidnatek AI Process Assistant"
)

st.caption(
    "Define the experiment you want to run. "
    "The assistant searches the complete Section A "
    "historical database and learns from Grade 4 results."
)

metric1, metric2 = st.columns(
    2
)

with metric1:
    st.metric(
        "Experiments Available to Memory",
        len(records),
    )

with metric2:
    st.metric(
        "Optimization Target",
        "Grade 4 / 4",
    )

st.info(
    "Project and formulation are optional context. "
    "The search itself can learn across the entire database."
)

st.write("---")
st.header(
    "1️⃣ Define Target Experiment"
)


# -----------------------------
# PRIMARY TECHNICAL INPUTS
# -----------------------------
material_options = (
    clean_material_options(
        records
    )
)

solvent_options = (
    clean_solvent_options(
        records
    )
)

machine_options = (
    clean_machine_options(
        records
    )
)

col1, col2, col3 = st.columns(
    3
)

with col1:
    material = resolve_select_or_custom(
        label="Polymer / Material",
        options=material_options,
        any_label="Any Polymer",
        custom_label="Custom / New Polymer or Material",
        key_prefix="material",
    )

with col2:
    solvent = resolve_select_or_custom(
        label="Solvent",
        options=solvent_options,
        any_label="Any Solvent",
        custom_label="Custom / New Solvent",
        key_prefix="solvent",
    )

with col3:
    machine = resolve_select_or_custom(
        label="Machine",
        options=machine_options,
        any_label="Any Machine",
        custom_label="Custom / New Machine",
        key_prefix="machine",
    )


# -----------------------------
# OPTIONAL CONTEXT
# -----------------------------
with st.expander(
    "Optional project / formulation context",
    expanded=False,
):
    st.caption(
        "Use these only when you want to narrow or "
        "boost the search. Internal migration IDs are hidden."
    )

    project_options = (
        clean_project_options(
            records
        )
    )

    formula_options = (
        clean_formula_options(
            records
        )
    )

    context_col1, context_col2 = (
        st.columns(2)
    )

    with context_col1:
        project_code = (
            resolve_select_or_custom(
                label="Project Context",
                options=project_options,
                any_label="All Projects",
                custom_label="Custom / New Project Context",
                key_prefix="project",
            )
        )

    with context_col2:
        formula_id = (
            resolve_select_or_custom(
                label="Formulation Context",
                options=formula_options,
                any_label="Any Formulation",
                custom_label="Custom / New Formulation",
                key_prefix="formula",
            )
        )


# -----------------------------
# PROCESS PARAMETERS
# -----------------------------
st.subheader(
    "Critical Process Parameters"
)

with st.form(
    "search_form"
):
    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:
        flow = st.number_input(
            "Q1 (mL/h)",
            value=1.0,
            step=0.1,
        )

        hv_plus = st.number_input(
            "HV+ (kV)",
            value=15.0,
            step=0.1,
        )

    with col2:
        hv_minus = st.number_input(
            "HV- (kV)",
            value=0.0,
            step=0.1,
        )

        temperature = (
            st.number_input(
                "T (°C)",
                value=25.0,
                step=0.1,
            )
        )

    with col3:
        humidity = st.number_input(
            "RH (%)",
            value=40.0,
            step=0.1,
        )

        dz = st.number_input(
            "dZ (mm)",
            value=150.0,
            step=1.0,
        )

    submitted = (
        st.form_submit_button(
            "🔍 Analyze Grade 4 Potential"
        )
    )


query = {
    "project_code":
        project_code,
    "formula_id":
        formula_id,
    "material":
        material,
    "solvent":
        solvent,
    "machine":
        machine,
    "flow":
        flow,
    "hv_plus":
        hv_plus,
    "hv_minus":
        hv_minus,
    "temperature":
        temperature,
    "humidity":
        humidity,
    "dz":
        dz,
}


if submitted:
    similar = (
        search_similar_experiments(
            records,
            query,
        )
    )

    st.session_state[
        "last_query"
    ] = query

    st.session_state[
        "similar_results"
    ] = similar


similar = st.session_state.get(
    "similar_results",
    [],
)

query_from_state = (
    st.session_state.get(
        "last_query",
        query,
    )
)


# ============================================================
# ASSESSMENT
# ============================================================
if similar:
    context_name = {
        4: "Exact formulation",
        3: "Same polymer + solvent",
        2: "Same polymer",
        1: "Global / solvent context",
    }.get(
        similar[0]["tier"],
        "Historical context",
    )

    st.success(
        f"{len(similar)} comparable historical "
        f"experiment(s) found. "
        f"Strongest context: {context_name}."
    )

    analysis = (
        analyze_similar_experiments(
            similar,
            query_from_state,
        )
    )

    st.subheader(
        "🎯 Grade 4 Process Assessment"
    )

    metric1, metric2, metric3, metric4 = (
        st.columns(4)
    )

    with metric1:
        st.metric(
            "Comparable Experiments",
            analysis["total"],
        )

    with metric2:
        st.metric(
            "Graded Experiments",
            analysis["graded"],
        )

    with metric3:
        st.metric(
            "Grade 4 Experiments",
            analysis["grade_4"],
        )

    with metric4:
        rate = analysis[
            "grade_4_rate"
        ]

        st.metric(
            "Grade 4 Success Rate",
            (
                f"{rate}%"
                if rate is not None
                else "No graded data"
            ),
        )

    st.write(
        "### Historical Expectation"
    )

    expected_grade = analysis[
        "expected_grade"
    ]

    if expected_grade is not None:
        st.metric(
            "Similarity-weighted Expected Grade",
            f"{expected_grade} / 4",
        )
    else:
        st.warning(
            "Not enough graded historical "
            "data for an estimate."
        )

    st.info(
        analysis["interpretation"]
    )

    st.write(
        "### Grade 4 Historical Process Window"
    )

    process_window_rows = []

    for (
        parameter,
        statistics,
    ) in analysis[
        "process_window"
    ].items():
        if statistics is None:
            continue

        process_window_rows.append(
            {
                "Parameter":
                    parameter,
                "Minimum":
                    statistics["minimum"],
                "Maximum":
                    statistics["maximum"],
                "Grade 4 Average":
                    statistics["average"],
            }
        )

    if process_window_rows:
        st.dataframe(
            pd.DataFrame(
                process_window_rows
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.write(
            "### Recommended Next Experiment"
        )

        recommendation = analysis[
            "recommendation"
        ]

        recommendation_columns = (
            st.columns(3)
        )

        for (
            index,
            (
                label,
                value,
            ),
        ) in enumerate(
            recommendation.items()
        ):
            with recommendation_columns[
                index % 3
            ]:
                st.metric(
                    label,
                    value,
                )

        st.caption(
            "Recommendation = historical average "
            "of the strongest comparable Grade 4 experiments. "
            "Decision support only; not a guaranteed prediction."
        )
    else:
        st.warning(
            "No Grade 4 process window is available "
            "for this context yet."
        )

    if analysis["warnings"]:
        st.write(
            "### Risk Warnings"
        )

        for warning in analysis[
            "warnings"
        ]:
            st.warning(
                warning
            )

    if analysis["comments"]:
        st.write(
            "### Historical Engineer Comments"
        )

        for comment in analysis[
            "comments"
        ]:
            st.write(
                f"- {comment}"
            )

elif submitted:
    st.warning(
        "No scientifically comparable historical "
        "experiments were found. Try a broader material, "
        "solvent or machine context."
    )


# ============================================================
# EVIDENCE
# ============================================================
st.write("---")
st.header(
    "2️⃣ Evidence"
)

if st.button(
    "📊 Show Comparable Experiments"
):
    if similar:
        tier_names = {
            4:
                "Exact formulation",
            3:
                "Same polymer + solvent",
            2:
                "Same polymer",
            1:
                "Global / solvent context",
        }

        evidence_rows = []

        for item in similar:
            row = (
                summarize_experiment(
                    item["experiment"]
                )
            )

            row[
                "context_match"
            ] = tier_names.get(
                item["tier"],
                "",
            )

            row[
                "similarity_score_%"
            ] = item["score"]

            evidence_rows.append(
                row
            )

        st.dataframe(
            pd.DataFrame(
                evidence_rows
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning(
            "Run the Grade 4 analysis first."
        )


# ============================================================
# TRACEABILITY
# ============================================================
st.write("---")
st.header(
    "3️⃣ Save / Traceability"
)

st.info(
    "New experimental data is saved through Section A: "
    "Projects → Materials → Formulations → Setups → "
    "Experimental Runs → Results."
)


# ============================================================
# MEMORY
# ============================================================
st.write("---")
st.header(
    "4️⃣ Experiment Memory"
)

if records:
    st.dataframe(
        pd.DataFrame(
            [
                summarize_experiment(
                    experiment
                )
                for experiment in records
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info(
        "No experiments are available."
    )