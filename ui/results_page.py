import streamlit as st
import uuid

from database.entities import Result

from database.section_a_database import (
    add_result,
    list_results,
    list_runs,
)


def render_results_page():
    st.title("Results")

    runs = list_runs()
    results = list_results()

    # -----------------------------
    # EXISTING RESULTS
    # -----------------------------
    st.subheader("Existing Results")

    if results:
        result_labels = {
            (
                f"{result.get('run_id', '')} | "
                f"{result.get('result_id', '')[:8]}"
            ): result
            for result in results
        }

        selected_result_label = st.selectbox(
            "Select Result",
            list(result_labels.keys())
        )

        selected_result = result_labels[
            selected_result_label
        ]

        st.write("### Result Details")
        st.json(selected_result)

    else:
        st.info(
            "No results have been created yet."
        )

    st.write("---")

    # -----------------------------
    # ADD RESULT
    # -----------------------------
    st.subheader("Add Result to Experimental Run")

    if not runs:
        st.warning(
            "No experimental runs are available. "
            "Create a run before adding results."
        )
        return

    run_options = {
        (
            f"{run.get('sample_code', '')} | "
            f"{run.get('date', '')}"
        ): run
        for run in runs
    }

    with st.form("create_result_form"):

        run_label = st.selectbox(
            "Experimental Run",
            list(run_options.keys())
        )

        sem_morphology = st.text_area(
            "SEM Morphology"
        )

        filtration_performance = st.text_area(
            "Filtration Performance"
        )

        notes = st.text_area(
            "Result Notes"
        )

        result_submitted = st.form_submit_button(
            "Save Result"
        )

    if result_submitted:

        selected_run = run_options[
            run_label
        ]

        run_id = selected_run[
            "run_id"
        ]

        # Prevent duplicate result record
        existing_result_for_run = any(
            result.get("run_id") == run_id
            for result in results
        )

        if existing_result_for_run:
            st.error(
                "A result record already exists "
                "for this experimental run."
            )
            return

        has_result_data = any([
            sem_morphology.strip(),
            filtration_performance.strip(),
            notes.strip(),
        ])

        if not has_result_data:
            st.error(
                "Enter at least one result field "
                "before saving."
            )
            return

        result = Result(
            result_id=str(uuid.uuid4()),
            run_id=run_id,
            sem_morphology=sem_morphology.strip(),
            filtration_performance=filtration_performance.strip(),
            notes=notes.strip(),
        )

        try:
            add_result(result)

            st.success(
                "Result saved successfully."
            )

            st.rerun()

        except ValueError as error:
            st.error(str(error))