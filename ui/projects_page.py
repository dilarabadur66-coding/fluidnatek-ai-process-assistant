import streamlit as st
import uuid
from datetime import datetime

from database.entities import Project
from database.section_a_database import (
    add_project,
    list_projects,
)


def render_projects_page():
    st.title("Projects")

    projects = list_projects()

    st.subheader("Existing Projects")

    if projects:
        project_labels = {
            f"{project.get('project_code', '')} - {project.get('client', '')}":
            project
            for project in projects
        }

        selected_label = st.selectbox(
            "Select Project",
            list(project_labels.keys())
        )

        selected_project = project_labels[selected_label]

        st.write("### Project Details")

        st.json(selected_project)

        if st.button("Set as Active Project"):
            st.session_state["active_project"] = selected_project

            st.success(
                f"Active project set to: "
                f"{selected_project.get('project_code', '')}"
            )

    else:
        st.info("No projects have been created yet.")

    st.write("---")

    st.subheader("Create New Project")

    with st.form("create_project_form"):
        col1, col2 = st.columns(2)

        with col1:
            project_code = st.text_input("Project Code")
            beas_code = st.text_input("BEAS Code")
            client = st.text_input("Client")

        with col2:
            rd_leader = st.text_input("R&D Leader")
            year = st.number_input(
                "Year",
                min_value=2000,
                max_value=2100,
                value=datetime.now().year,
                step=1
            )

        submitted = st.form_submit_button(
            "Create Project"
        )

    if submitted:
        if not project_code.strip():
            st.error("Project Code is required.")
            return

        project = Project(
            project_id=str(uuid.uuid4()),
            project_code=project_code.strip(),
            beas_code=beas_code.strip(),
            client=client.strip(),
            rd_leader=rd_leader.strip(),
            year=int(year),
        )

        try:
            add_project(project)

            st.success(
                f"Project created successfully: {project_code}"
            )

            st.rerun()

        except ValueError as error:
            st.error(str(error))