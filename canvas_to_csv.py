"""Script to export Canvas tasks to a CSV file."""

import csv
from datetime import datetime

import pytz
import requests

API_URL = "https://canvas.cmu.edu/api/v1"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"


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


def export_to_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=["Course ID", "Course Name", "Assignment", "Due Date"]
        )
        writer.writeheader()
        writer.writerows(data)


def main():
    tasks = []
    assignments = get_assignments()
    for assignment in assignments:
        if assignment["plannable_type"] == "assignment" or assignment["plannable_type"] == "quiz":
            # Convert due date from UTC to ET
            utc_time = datetime.strptime(assignment["plannable"]["due_at"], "%Y-%m-%dT%H:%M:%SZ")
            utc_time = utc_time.replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(tz=pytz.timezone("US/Eastern"))
            tasks.append(
                {
                    "Course ID": assignment["course_id"],
                    "Course Name": assignment["context_name"],
                    "Assignment": assignment["plannable"]["title"],
                    "Due Date": local_time.strftime("%b %d at %I:%M %p"),
                }
            )

    export_to_csv(tasks, "canvas_tasks.csv")
    print("Tasks exported")


if __name__ == "__main__":
    main()
