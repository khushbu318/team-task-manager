import base64
import json

import streamlit as st

from api_client import APIClient


st.set_page_config(
    page_title="Team Task Manager",
    layout="wide",
)


if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None


def decode_jwt_payload(token: str):

    try:
        payload = token.split(".")[1]

        padding = "=" * (
            4 - len(payload) % 4
        )

        decoded = base64.urlsafe_b64decode(
            payload + padding
        )

        return json.loads(
            decoded.decode("utf-8")
        )

    except Exception:
        return {}


st.title("Team Task Manager")

st.caption(
    "FastAPI + SQLModel + JWT + RBAC + Streamlit"
)


if not st.session_state.token:

    st.subheader("Login")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password",
    )

    if st.button("Login"):

        client = APIClient()

        try:

            result = client.login(
                username,
                password,
            )

            st.session_state.token = (
                result["access_token"]
            )

            st.session_state.username = (
                username
            )

            st.rerun()

        except Exception as exc:

            st.error(
                f"Login failed: {exc}"
            )

else:

    token = st.session_state.token

    payload = decode_jwt_payload(token)

    role = payload.get(
        "role",
        "unknown",
    )

    user_id = payload.get(
        "sub",
        "unknown",
    )

    st.sidebar.success(
        f"Logged in as: {st.session_state.username}"
    )

    st.sidebar.write(
        f"User ID: {user_id}"
    )

    st.sidebar.write(
        f"Role: {role}"
    )

    if st.sidebar.button("Logout"):

        st.session_state.token = None
        st.session_state.username = None

        st.rerun()

    client = APIClient(token)

    st.header("JWT + RBAC Dashboard")

    # -------------------------------------------------
    # JWT SECTION
    # -------------------------------------------------

    st.subheader("1. What is inside the JWT?")

    st.json(payload)

    # -------------------------------------------------
    # AUTHORIZATION FLOW
    # -------------------------------------------------

    st.subheader("2. Request Pipeline")

    steps = [
        "Streamlit sends HTTP request",
        "Authorization: Bearer <JWT>",
        "FastAPI extracts token",
        "JWT signature is verified",
        "JWT payload is decoded",
        "User is loaded from database",
        "RBAC / ownership rules are checked",
        "Service executes business logic",
        "Repository talks to SQLModel",
        "Database returns data",
    ]

    for index, step in enumerate(
        steps,
        start=1,
    ):

        st.write(
            f"**{index}.** {step}"
        )

    # -------------------------------------------------
    # TASKS
    # -------------------------------------------------

    st.subheader("3. My Tasks")

    try:

        tasks = client.get_tasks()

        if not tasks:

            st.info(
                "No tasks available."
            )

        for task in tasks:

            with st.container(
                border=True
            ):

                st.write(
                    f"### #{task['id']} "
                    f"{task['title']}"
                )

                st.write(
                    f"Status: "
                    f"**{task['status']}**"
                )

                if task["description"]:
                    st.write(
                        task["description"]
                    )

                if task["current_state"]:
                    st.write(
                        "Stage: "
                        f"{task['current_state']}"
                    )

                if task["blocker"]:
                    st.warning(
                        "Blocker: "
                        f"{task['blocker']}"
                    )

                if task["permission_issue"]:
                    st.error(
                        "Permission issue: "
                        f"{task['permission_issue']}"
                    )

                # Developers can update their own tasks.
                # Team leads can update any task.
                with st.form(
                    f"update_{task['id']}"
                ):

                    status = st.selectbox(
                        "Status",
                        [
                            "todo",
                            "in_progress",
                            "blocked",
                            "completed",
                        ],
                        index=[
                            "todo",
                            "in_progress",
                            "blocked",
                            "completed",
                        ].index(
                            task["status"]
                        ),
                    )

                    stage = st.text_input(
                        "Current stage",
                        value=(
                            task["current_state"]
                            or ""
                        ),
                    )

                    blocker = st.text_input(
                        "Blocker",
                        value=(
                            task["blocker"]
                            or ""
                        ),
                    )

                    permission_issue = (
                        st.text_input(
                            "Permission issue",
                            value=(
                                task[
                                    "permission_issue"
                                ]
                                or ""
                            ),
                        )
                    )

                    submitted = st.form_submit_button(
                        "Update Task"
                    )

                    if submitted:

                        response = (
                            client.update_task(
                                task["id"],
                                {
                                    "status": status,
                                    "current_state": (
                                        stage or None
                                    ),
                                    "blocker": (
                                        blocker or None
                                    ),
                                    "permission_issue": (
                                        permission_issue
                                        or None
                                    ),
                                },
                            )
                        )

                        if response.ok:

                            st.success(
                                "Task updated"
                            )

                            st.rerun()

                        else:

                            st.error(
                                response.text
                            )

    except Exception as exc:

        st.error(
            f"Could not load tasks: {exc}"
        )

    # -------------------------------------------------
    # TEAM LEAD AREA
    # -------------------------------------------------

    if role == "team_lead":

        st.divider()

        st.subheader(
            "4. Team Lead: Create Task"
        )

        with st.form("create_task"):

            title = st.text_input(
                "Task title"
            )

            description = st.text_area(
                "Description"
            )

            assignee_id = st.number_input(
                "Developer User ID",
                min_value=1,
                step=1,
            )

            submitted = st.form_submit_button(
                "Create Task"
            )

            if submitted:

                response = (
                    client.create_task(
                        title=title,
                        description=description,
                        assignee_id=int(
                            assignee_id
                        ),
                    )
                )

                if response.ok:

                    st.success(
                        "Task created"
                    )

                    st.rerun()

                else:

                    st.error(
                        response.text
                    )

    else:

        st.divider()

        st.info(
            "Developer role: task creation "
            "is disabled."
        )
