# Canvas Tasks to Google Tasks

Steps to use the script:
1. Install the required python packages in a venv using `pip install -r requirements.txt`
2. Obtain a Canvas API key from your Canvas account and save it in an environment variable named `CANVAS_ACCESS_TOKEN`.
3. Create a Google OAuth 2.0 Client ID by following the instructions [here](https://developers.google.com/tasks/reference/rest/v1/tasks/insert#authorization-scopes) and save the client secret file in this directory.
4. Run the `generate_google_credentials.py` script to generate your Google auth credentials. Save the generated `client_id`, `client_secret`, and `refresh_token` in environment variables named `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN` respectively.
5. Run the script with your preferred start and end dates.

Sample usage:
```sh
python canvas_to_tasks.py --start-date "2025-04-01" --end-date "2025-04-30" --create-tasks
```
