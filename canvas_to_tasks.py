"""Script to fetch assignments from Canvas and create tasks in Google Tasks."""

import json
from datetime import datetime

import pytz
import requests
from google_auth_oauthlib.flow import InstalledAppFlow

# Canvas API config
API_URL = "https://canvas.cmu.edu/api/v1"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

# Google Tasks API config
CLIENT_FILE = "path/to/client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/tasks"]


def get_assignments():
    assignments_url = f"{API_URL}/planner/items"
    params = {
        "start_date": "2025-01-12",
        "end_date": "2025-01-21",
        "per_page": 100,
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    assignments = []

    response = requests.get(assignments_url, params=params, headers=headers)
    response.raise_for_status()
    assignments = response.json()

    return assignments


def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials.token


def create_tasks(tasks):
    token = authenticate()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    for task in tasks:
        response = requests.post(
            "https://tasks.googleapis.com/tasks/v1/lists/@default/tasks",
            headers=headers,
            data=json.dumps(task),
        )
        response.raise_for_status()
        print("Task created successfully")


def parse_tasks(assignments):
    tasks = []
    for assignment in assignments:
        if assignment["plannable_type"] == "assignment" or assignment["plannable_type"] == "quiz":
            # Convert due date from UTC to ET
            utc_time = datetime.strptime(assignment["plannable"]["due_at"], "%Y-%m-%dT%H:%M:%SZ")
            utc_time = utc_time.replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(tz=pytz.timezone("US/Eastern"))
            tasks.append(
                {
                    "notes": assignment["context_name"],
                    "title": assignment["plannable"]["title"],
                    "due": local_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
    return tasks


def main():
    assignments = get_assignments()
    tasks = parse_tasks(assignments)
    create_tasks(tasks)


if __name__ == "__main__":
    main()
