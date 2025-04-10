from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/tasks"]


def generate_refresh_token(client_file_path):
    flow = InstalledAppFlow.from_client_secrets_file(client_file_path, SCOPES)
    credentials = flow.run_local_server(port=0, open_browser=False)
    print("Refresh Token:", credentials.refresh_token)
    print("Access Token:", credentials.token)
    print("Client ID:", credentials.client_id)
    print("Client Secret:", credentials.client_secret)


generate_refresh_token("client_secret.json")
