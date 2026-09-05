import requests


API_URL = "http://127.0.0.1:8000"


class APIClient:

    def __init__(
        self,
        token: str | None = None
    ):
        self.token = token

    @property
    def headers(self):

        if not self.token:
            return {}

        return {
            "Authorization": (
                f"Bearer {self.token}"
            )
        }

    # -------------------------------------------------
    # LOGIN
    # -------------------------------------------------

    def login(
        self,
        username: str,
        password: str,
    ):

        # OAuth2PasswordRequestForm expects
        # application/x-www-form-urlencoded data.
        #
        # Therefore use:
        #
        #     data={}
        #
        # NOT:
        #
        #     json={}
        #
        response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": username,
                "password": password,
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    # -------------------------------------------------
    # GET TASKS
    # -------------------------------------------------

    def get_tasks(self):

        response = requests.get(
            f"{API_URL}/tasks",
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    # -------------------------------------------------
    # CREATE TASK
    # -------------------------------------------------

    def create_task(
        self,
        title: str,
        description: str,
        assignee_id: int,
    ):

        response = requests.post(
            f"{API_URL}/tasks",
            headers=self.headers,
            json={
                "title": title,
                "description": description,
                "assignee_id": assignee_id,
            },
            timeout=10,
        )

        return response

    # -------------------------------------------------
    # UPDATE TASK
    # -------------------------------------------------

    def update_task(
        self,
        task_id: int,
        payload: dict,
    ):

        response = requests.patch(
            f"{API_URL}/tasks/{task_id}",
            headers=self.headers,
            json=payload,
            timeout=10,
        )

        return response