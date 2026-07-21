import streamlit as st
import uuid

from database.entities import (
    InjectorModel,
    CollectorModel,
    Setup,
)

from database.section_a_database import (
    add_injector_model,
    add_collector_model,
    add_setup,
    list_injector_models,
    list_collector_models,
    list_setups,
)


def render_setups_page():
    st.title("Setups")

    injector_models = list_injector_models()
    collector_models = list_collector_models()
    setups = list_setups()

    # -----------------------------
    # EXISTING SETUPS
    # -----------------------------
    st.subheader("Existing Setups")

    if setups:
        setup_labels = {
            (
                f"{setup.get('name', '')} | "
                f"{setup.get('machine', '')}"
            ): setup
            for setup in setups
        }

        selected_setup_label = st.selectbox(
            "Select Setup",
            list(setup_labels.keys())
        )

        selected_setup = setup_labels[
            selected_setup_label
        ]

        st.write("### Setup Details")
        st.json(selected_setup)

    else:
        st.info("No setups have been created yet.")

    st.write("---")

    # -----------------------------
    # INJECTOR MODELS
    # -----------------------------
    st.subheader("Injector Models")

    if injector_models:
        injector_labels = {
            injector.get("name", ""): injector
            for injector in injector_models
        }

        selected_injector_label = st.selectbox(
            "Existing Injector Models",
            list(injector_labels.keys())
        )

        st.json(
            injector_labels[selected_injector_label]
        )

    with st.form("create_injector_model_form"):
        injector_name = st.text_input(
            "Injector Model Name"
        )

        injector_description = st.text_area(
            "Injector Description"
        )

        injector_submitted = st.form_submit_button(
            "Create Injector Model"
        )

    if injector_submitted:
        if not injector_name.strip():
            st.error(
                "Injector Model Name is required."
            )
        else:
            injector_model = InjectorModel(
                injector_model_id=str(uuid.uuid4()),
                name=injector_name.strip(),
                description=injector_description.strip(),
            )

            try:
                add_injector_model(
                    injector_model
                )

                st.success(
                    "Injector model created successfully."
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))

    st.write("---")

    # -----------------------------
    # COLLECTOR MODELS
    # -----------------------------
    st.subheader("Collector Models")

    if collector_models:
        collector_labels = {
            collector.get("name", ""): collector
            for collector in collector_models
        }

        selected_collector_label = st.selectbox(
            "Existing Collector Models",
            list(collector_labels.keys())
        )

        st.json(
            collector_labels[
                selected_collector_label
            ]
        )

    with st.form("create_collector_model_form"):
        collector_name = st.text_input(
            "Collector Model Name"
        )

        collector_description = st.text_area(
            "Collector Description"
        )

        collector_submitted = st.form_submit_button(
            "Create Collector Model"
        )

    if collector_submitted:
        if not collector_name.strip():
            st.error(
                "Collector Model Name is required."
            )
        else:
            collector_model = CollectorModel(
                collector_model_id=str(uuid.uuid4()),
                name=collector_name.strip(),
                description=collector_description.strip(),
            )

            try:
                add_collector_model(
                    collector_model
                )

                st.success(
                    "Collector model created successfully."
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))

    st.write("---")

    # -----------------------------
    # CREATE FLEXIBLE SETUP
    # -----------------------------
    st.subheader("Create Flexible Setup")

    injector_models = list_injector_models()
    collector_models = list_collector_models()

    injector_options = {
        injector.get("name", ""): injector
        for injector in injector_models
    }

    collector_options = {
        collector.get("name", ""): collector
        for collector in collector_models
    }

    with st.form("create_setup_form"):
        setup_name = st.text_input(
            "Setup Name"
        )

        machine = st.text_input(
            "Machine"
        )

        col1, col2 = st.columns(2)

        with col1:
            injector_label = st.selectbox(
                "Injector Model",
                list(injector_options.keys())
                if injector_options
                else [""]
            )

            number_of_needles = st.number_input(
                "Number of Needles",
                min_value=1,
                value=1,
                step=1
            )

            needle_gauge = st.text_input(
                "Needle Gauge"
            )

        with col2:
            collector_label = st.selectbox(
                "Collector Model",
                list(collector_options.keys())
                if collector_options
                else [""]
            )

            platform = st.text_input(
                "Platform"
            )

            custom_configuration_text = (
                st.text_area(
                    "Custom Configuration Details"
                )
            )

        notes = st.text_area(
            "Setup Notes"
        )

        setup_submitted = st.form_submit_button(
            "Create Setup"
        )

    if setup_submitted:
        if not setup_name.strip():
            st.error(
                "Setup Name is required."
            )
            return

        if not injector_options:
            st.error(
                "At least one injector model is required."
            )
            return

        if not collector_options:
            st.error(
                "At least one collector model is required."
            )
            return

        selected_injector = injector_options[
            injector_label
        ]

        selected_collector = collector_options[
            collector_label
        ]

        setup = Setup(
            setup_id=str(uuid.uuid4()),
            name=setup_name.strip(),
            machine=machine.strip(),
            injector_model_id=selected_injector[
                "injector_model_id"
            ],
            collector_model_id=selected_collector[
                "collector_model_id"
            ],
            number_of_needles=int(
                number_of_needles
            ),
            needle_gauge=needle_gauge.strip(),
            platform=platform.strip(),
            custom_configuration={
                "details":
                custom_configuration_text.strip()
            },
            notes=notes.strip(),
        )

        try:
            add_setup(setup)

            st.success(
                f"Setup created successfully: "
                f"{setup_name}"
            )

            st.rerun()

        except ValueError as error:
            st.error(str(error))