# Canvas Tasks to Google Tasks

Steps to use the script:
1. Install the required packages:
```sh
pip install -r requirements.txt
```
2. Obtain a Canvas API key from your Canvas account and save it in an environment variable named `CANVAS_ACCESS_TOKEN`.
3. Create a Google OAuth 2.0 Client ID by following the instructions [here](https://developers.google.com/tasks/reference/rest/v1/tasks/insert#authorization-scopes) and save the client secret file in a location of your choice.
4. Run the script with your preffered start and end dates.

Sample usage:
```sh
python canvas_to_tasks.py --start-date "2025-01-19" --end-date "2025-01-28" --create-tasks --client-file-path "path/to/client_secret.json"
```
