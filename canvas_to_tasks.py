"""Script to fetch assignments from Canvas and create tasks in Google Tasks."""

import json
import logging
import pprint
from datetime import datetime

import click
import pytz
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Canvas API config
CANVAS_API_URL = "https://canvas.cmu.edu/api/v1"

# Google Tasks API config
SCOPES = ["https://www.googleapis.com/auth/tasks"]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_assignments(canvas_access_token, start_date, end_date):
    """Fetch assignments from Canvas for a given date range.

    Args:
        canvas_access_token (str): Canvas access token.
        start_date (str): Start date in the format YYYY-MM-DD.
        end_date (str): End date in the format YYYY-MM-DD.
    """
    assignments_url = f"{CANVAS_API_URL}/planner/items"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "per_page": 100,
    }
    headers = {"Authorization": f"Bearer {canvas_access_token}"}
    assignments = []

    response = requests.get(assignments_url, params=params, headers=headers)
    response.raise_for_status()
    assignments = response.json()

    return assignments


def parse_tasks(assignments):
    """Parse assignments and quizzes from Canvas into tasks for Google Tasks.

    Args:
        assignments (list): List of assignments and quizzes from Canvas.
    """
    tasks = []
    for assignment in assignments:
        if assignment["plannable_type"] == "assignment" or assignment["plannable_type"] == "quiz":
            # Ignore completed assignments
            if assignment["submissions"]["submitted"]:
                continue
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


def google_authenticate_with_refresh_token(client_id, client_secret, refresh_token):
    """Authenticate with Google using a refresh token.

    Args:
        client_id (str): Google OAuth client ID.
        client_secret (str): Google OAuth client secret.
        refresh_token (str): Refresh token for Google OAuth.
    """
    credentials = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )
    credentials.refresh(Request())
    return credentials.token


def create_google_tasks(tasks, client_id, client_secret, refresh_token):
    """Create tasks in Google Tasks.

    Args:
        tasks (list): List of tasks to create in Google Tasks.
        client_id (str): Google OAuth client ID.
        client_secret (str): Google OAuth client secret.
        refresh_token (str): Refresh token for Google OAuth.
    """
    token = google_authenticate_with_refresh_token(client_id, client_secret, refresh_token)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    for task in tasks:
        response = requests.post(
            "https://tasks.googleapis.com/tasks/v1/lists/@default/tasks",
            headers=headers,
            data=json.dumps(task),
        )
        response.raise_for_status()
        logger.info("Task created successfully for: %s", task["title"])


@click.command()
@click.option(
    "--canvas-access-token",
    "canvas_access_token",
    envvar="CANVAS_ACCESS_TOKEN",
    type=str,
    required=True,
    help="Canvas access token",
)
@click.option(
    "--start-date",
    "start_date",
    type=str,
    required=True,
    help="Start date in the format YYYY-MM-DD",
)
@click.option(
    "--end-date",
    "end_date",
    type=str,
    required=True,
    help="End date in the format YYYY-MM-DD",
)
@click.option("--create-tasks", "create_tasks", is_flag=True, help="Create tasks in Google Tasks")
@click.option(
    "--client-id",
    "client_id",
    envvar="GOOGLE_CLIENT_ID",
    type=str,
    help="Google OAuth client ID",
)
@click.option(
    "--client-secret",
    "client_secret",
    envvar="GOOGLE_CLIENT_SECRET",
    type=str,
    help="Google OAuth client secret",
)
@click.option(
    "--refresh-token",
    "refresh_token",
    envvar="GOOGLE_REFRESH_TOKEN",
    type=str,
    help="Google OAuth refresh token",
)
def cli(
    canvas_access_token, start_date, end_date, create_tasks, client_id, client_secret, refresh_token
):
    """Fetch assignments from Canvas and create tasks in Google Tasks.

    Args:
        canvas_access_token (str): Canvas access token.
        start_date (str): Start date in the format YYYY-MM-DD.
        end_date (str): End date in the format YYYY-MM-DD.
        create_tasks (bool): Create tasks in Google Tasks.
        client_id (str): Google OAuth client ID.
        client_secret (str): Google OAuth client secret.
        refresh_token (str): Google OAuth refresh token.
    """
    assignments = get_assignments(canvas_access_token, start_date, end_date)
    tasks = parse_tasks(assignments)
    logger.info("Parsed tasks: %s", pprint.pformat(tasks))
    if create_tasks:
        create_google_tasks(tasks, client_id, client_secret, refresh_token)


if __name__ == "__main__":
    cli()
