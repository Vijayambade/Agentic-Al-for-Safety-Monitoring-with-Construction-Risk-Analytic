"""
=========================================================
Projects Page
=========================================================
"""

import streamlit as st
from core.document_analyzer import (extract_document_text,analyze_document,)
from core import database as db
# =========================================================
# SESSION STATE
# =========================================================

if "show_add_project" not in st.session_state:
    st.session_state.show_add_project = False

if "upload_mode" not in st.session_state:
    st.session_state.upload_mode = False

if "projects" not in st.session_state:

    # Projects are loaded from the SQLite database. On first
    # ever run the database is empty, so the same 3 demo
    # projects that used to be hard-coded here are seeded
    # automatically (see core/database.get_or_seed_projects).
    st.session_state["projects"] = db.get_or_seed_projects()


# =========================================================
# PROJECT PAGE
# =========================================================

def render_projects():

    # ----------------------------------------------------
    # HEADER
    # ----------------------------------------------------

    left, right = st.columns([5,1])

    with left:

        st.title("Projects")
        st.caption("Manage all construction projects.")

    with right:

        st.write("")
        st.write("")

        if st.button(
            "➕ Add Project",
            use_container_width=True,
            key="top_add_project",
        ):

            st.session_state.show_add_project = True

    st.divider()

    # ----------------------------------------------------
    # SEARCH
    # ----------------------------------------------------

    col1,col2 = st.columns([3,1])

    with col1:

        search = st.text_input(
            "🔍 Search Projects",
            placeholder="Search by project name...",
        )

    with col2:

        status_filter = st.selectbox(

            "Status",

            [
                "All",
                "Planning",
                "Active",
                "Completed",
                "Delayed",
            ],

        )

    filtered_projects = []

    for project in st.session_state.get("projects", []):

        if search.lower() in project["name"].lower():

            if status_filter == "All" or project["status"] == status_filter:

                filtered_projects.append(project)

    # ----------------------------------------------------
    # ADD PROJECT
    # ----------------------------------------------------

    if st.session_state.show_add_project:

        st.markdown("---")

        st.subheader("➕ Add New Project")

        with st.form("project_form"):

            c1,c2 = st.columns(2)

            with c1:

                project_name = st.text_input("Project Name")
                client = st.text_input("Client")
                location = st.text_input("Location")
                engineer = st.text_input("Engineer")

            with c2:

                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")

                budget = st.number_input(
                    "Budget (₹)",
                    min_value=0.0,
                )

                project_status = st.selectbox(

                    "Status",

                    [
                        "Planning",
                        "Active",
                        "Completed",
                        "Delayed",
                    ],

                )

            progress = st.slider(
                "Progress (%)",
                0,
                100,
                0,
            )

            col1,col2 = st.columns(2)

            with col1:

                save = st.form_submit_button(
                    "Save Project",
                    use_container_width=True,
                )

            with col2:

                cancel = st.form_submit_button(
                    "Cancel",
                    use_container_width=True,
                )

        if save:

            new_project = {
                "name": project_name,
                "client": client,
                "location": location,
                "engineer": engineer,
                "start_date": start_date,
                "end_date": end_date,
                "status": project_status,
                "progress": progress,
                "budget": budget,
            }

            # Persist to the database and keep the id it was
            # given, so future edits/deletes update the same row.
            new_id = db.add_project(new_project)
            new_project["id"] = new_id

            st.session_state["projects"].append(new_project)
            st.session_state.recent_activity.insert(
                0,
                f"Added project: {project_name}"
            )
            st.session_state.recent_activity = (
                st.session_state.recent_activity[:10]
            )
            

            st.success(" Project Added Successfully!")

            st.session_state.show_add_project = False

            st.rerun()

        if cancel:

            st.session_state.show_add_project = False

            st.rerun()

    # ----------------------------------------------------
    # UPLOAD DRAWING
    # ----------------------------------------------------
    if st.session_state.upload_mode:
        st.markdown("---")
        st.subheader("Construction Document Analyzer")

        project_names = [
            project["name"]
            for project in st.session_state["projects"]
        ]

        selected_project = st.selectbox(
            "Select Project",project_names,
        )

        drawing = st.file_uploader(
            "Upload Drawing / BOQ / Contract",
            type=["pdf", "png", "jpg", "jpeg"],
        )

        if drawing is not None:
            st.success(f"{drawing.name} uploaded successfully."
            )
            if st.button(" Analyze Document",
                        use_container_width=True,
            ):
                with st.spinner("Reading document..."
                    ):
                    document_text = extract_document_text(drawing
                    )

                if document_text.strip() == "":
                    st.error(
                        "Unable to extract text from the document."
                    )

                else:
                    with st.spinner(
                        "Analyzing using Ollama..."
                    ):
                        analysis = analyze_document(
                            selected_project,
                            document_text,
                        )

                    st.success(
                        "Analysis Complete"
                    )

                    with st.container(border=True):
                        st.markdown(
                            "### 📑 AI Construction Analysis"
                        )

                        st.write(analysis)

    

    st.markdown("---")

    st.subheader(" Project Portfolio")
        # ----------------------------------------------------
    # PROJECT CARDS
    # ----------------------------------------------------

    if len(filtered_projects) == 0:

        st.info("No projects found.")

    else:

        for i, project in enumerate(filtered_projects):

            with st.container(border=True):

                col1, col2 = st.columns([4,1])

                # ----------------------------------------
                # Left Side
                # ----------------------------------------

                with col1:

                    st.markdown(f"###  {project['name']}")

                    st.write(f"**Client:** {project['client']}")

                    st.write(f"**Location:** {project['location']}")

                    st.write(f"**Status:** {project['status']}")

                    st.write("Progress")

                    st.progress(project["progress"]/100)

                    st.caption(
                        f"{project['progress']}% Completed"
                    )

                # ----------------------------------------
                # Right Side Buttons
                # ----------------------------------------

                with col2:
                    if st.button("✏ Edit",key=f"edit_{i}",use_container_width=True,):
                         st.session_state[f"editing_{i}"] = True

                    

                    if st.button( "🗑 Delete",key=f"delete_{i}", use_container_width=True,):
                        st.session_state[f"delete_confirm_{i}"] = True


                # ----------------------------------------
                # EDIT
                # ----------------------------------------

                if st.session_state.get(f"editing_{i}", False):

                    st.info("Edit Project")

                    new_name = st.text_input(
                        "Project Name",
                        value=project["name"],
                        key=f"name_{i}",
                    )

                    new_client = st.text_input(
                        "Client",
                        value=project["client"],
                        key=f"client_{i}",
                    )

                    new_location = st.text_input(
                        "Location",
                        value=project["location"],
                        key=f"location_{i}",
                    )

                    new_status = st.selectbox(
                        "Status",
                        [
                            "Planning",
                            "Active",
                            "Completed",
                            "Delayed",
                        ],
                        index=[
                            "Planning",
                            "Active",
                            "Completed",
                            "Delayed",
                        ].index(project["status"]),
                        key=f"status_{i}",
                    )

                    if st.button(
                        " Save Changes",
                        key=f"save_{i}",
                    ):
                        st.session_state["projects"][i]["name"] = new_name
                        st.session_state["projects"][i]["client"] = new_client
                        st.session_state["projects"][i]["location"] = new_location
                        st.session_state["projects"][i]["status"] = new_status

                        # Persist the change to the database.
                        project_id = st.session_state["projects"][i].get("id")
                        if project_id is not None:
                            db.update_project(
                                project_id,
                                st.session_state["projects"][i],
                            )

                        st.session_state.recent_activity.insert(
                             0,
                             f"✏ Updated project: {new_name}"
                             )
                        st.session_state.recent_activity = (
                            st.session_state.recent_activity[:10]
                        )
                        st.success("Project Updated Successfully!")
                        st.session_state[f"editing_{i}"] = False
                        st.rerun()

                # ----------------------------------------
                # DELETE
                # ----------------------------------------

                if st.session_state.get(f"delete_confirm_{i}", False):

                    st.warning(
                        "Are you sure you want to delete this project?"
                    )

                    c1, c2 = st.columns(2)

                    with c1:

                        if st.button(
                            "Yes",
                            key=f"yes_{i}",
                            use_container_width=True,
                        ):
                            deleted_project = st.session_state["projects"][i]["name"]

                            # Remove from the database too.
                            deleted_id = st.session_state["projects"][i].get("id")
                            if deleted_id is not None:
                                db.delete_project(deleted_id)

                            del st.session_state["projects"][i]
                            st.session_state.recent_activity.insert(
                                0,
                                f"🗑 Deleted project: {deleted_project}"
                            )
                            st.session_state.recent_activity = (
                                st.session_state.recent_activity[:10]
                            )
                            st.success("Project Deleted Successfully!")
                            st.session_state[f"delete_confirm_{i}"] = False
                            st.rerun()
                    with c2:
                            if st.button(
                                "Cancel",
                                key=f"cancel_{i}",
                                use_container_width=True,
                            ):
                                st.session_state[f"delete_confirm_{i}"] = False
                                st.rerun()

                st.write("")