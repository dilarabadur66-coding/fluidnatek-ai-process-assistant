import streamlit as st
import uuid
from datetime import date

from database.entities import Run

from database.section_a_database import (
    add_run,
    list_runs,
    list_projects,
    list_formulations,
    list_setups,
)


def render_runs_page():
    st.title("Experimental Runs")

    active_project = st.session_state.get("active_project")

    projects = list_projects()
    formulations = list_formulations()
    setups = list_setups()
    runs = list_runs()

    # --------------------------------
    # ACTIVE PROJECT
    # --------------------------------

    if active_project:
        st.info(
            f"Active Project: "
            f"{active_project.get('project_code', '')}"
        )
    else:
        st.warning(
            "No active project selected. "
            "Please select an active project from the Projects page."
        )

    # --------------------------------
    # EXISTING RUNS
    # --------------------------------

    st.subheader("Existing Experimental Runs")

    if runs:
        run_labels = {
            (
                f"{run.get('sample_code', '')} | "
                f"{run.get('date', '')}"
            ): run
            for run in runs
        }

        selected_run_label = st.selectbox(
            "Select Experimental Run",
            list(run_labels.keys())
        )

        selected_run = run_labels[
            selected_run_label
        ]

        st.write("### Run Details")
        st.json(selected_run)

    else:
        st.info(
            "No experimental runs have been created yet."
        )

    st.write("---")

    # --------------------------------
    # CREATE RUN
    # --------------------------------

    st.subheader("Create New Experimental Run")

    if not active_project:
        st.warning(
            "Select an active project before creating a run."
        )
        return

    # Only show formulations belonging
    # to the active project
    project_formulations = [
        formulation
        for formulation in formulations
        if formulation.get("project_id")
        == active_project.get("project_id")
    ]

    if not project_formulations:
        st.warning(
            "No formulations are available for the active project."
        )
        return

    if not setups:
        st.warning(
            "No setups are available. "
            "Create a setup before creating a run."
        )
        return

    formulation_options = {
        formulation.get("formulation_id", ""):
        formulation
        for formulation in project_formulations
    }

    setup_options = {
        (
            f"{setup.get('name', '')} | "
            f"{setup.get('machine', '')}"
        ): setup
        for setup in setups
    }

    with st.form("create_run_form"):

        st.write("### Experiment Identification")

        sample_code = st.text_input(
            "Sample Code"
        )

        experiment_date = st.date_input(
            "Experiment Date",
            value=date.today()
        )

        purpose = st.text_area(
            "Purpose"
        )

        st.write("### Experiment Configuration")

        col1, col2 = st.columns(2)

        with col1:

            formulation_label = st.selectbox(
                "Formulation",
                list(formulation_options.keys())
            )

        with col2:

            setup_label = st.selectbox(
                "Setup",
                list(setup_options.keys())
            )

        st.write("### Process Parameters")

        col1, col2, col3 = st.columns(3)

        with col1:

            flow_rate = st.number_input(
                "Flow Rate Q1 (mL/h)",
                min_value=0.0,
                value=0.0,
                step=0.1
            )

            injector_voltage = st.number_input(
                "Injector Voltage HV+ (kV)",
                value=0.0,
                step=0.1
            )

            collector_voltage = st.number_input(
                "Collector Voltage HV- (kV)",
                value=0.0,
                step=0.1
            )

        with col2:

            temperature = st.number_input(
                "Temperature (°C)",
                value=25.0,
                step=0.1
            )

            relative_humidity = st.number_input(
                "Relative Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=40.0,
                step=0.1
            )

            working_distance = st.number_input(
                "Working Distance dZ (mm)",
                min_value=0.0,
                value=0.0,
                step=0.1
            )

        with col3:

            drum_speed = st.number_input(
                "Drum Speed (rpm)",
                min_value=0.0,
                value=0.0,
                step=1.0
            )

            processability_score = st.number_input(
                "Processability Score",
                min_value=0,
                max_value=5,
                value=0,
                step=1
            )

        process_comments = st.text_area(
            "Process Comments"
        )

        run_submitted = st.form_submit_button(
            "Create Experimental Run"
        )

    # --------------------------------
    # SAVE RUN
    # --------------------------------

    if run_submitted:

        if not sample_code.strip():
            st.error(
                "Sample Code is required."
            )
            return

        # Prevent duplicate sample codes
        duplicate_sample = any(
            run.get("sample_code") == sample_code.strip()
            for run in runs
        )

        if duplicate_sample:
            st.error(
                "This Sample Code already exists."
            )
            return

        selected_formulation = formulation_options[
            formulation_label
        ]

        selected_setup = setup_options[
            setup_label
        ]

        run = Run(
            run_id=str(uuid.uuid4()),

            sample_code=sample_code.strip(),

            project_id=active_project[
                "project_id"
            ],

            formulation_id=selected_formulation[
                "formulation_id"
            ],

            setup_id=selected_setup[
                "setup_id"
            ],

            date=str(experiment_date),

            purpose=purpose.strip(),

            flow_rate=flow_rate,

            injector_voltage=injector_voltage,

            collector_voltage=collector_voltage,

            relative_humidity=relative_humidity,

            temperature=temperature,

            drum_speed=drum_speed,

            working_distance=working_distance,

            processability_score=processability_score,

            process_comments=process_comments.strip(),
        )

        try:

            add_run(run)

            st.success(
                f"Experimental run created successfully: "
                f"{sample_code}"
            )

            st.rerun()

        except ValueError as error:

            st.error(str(error))