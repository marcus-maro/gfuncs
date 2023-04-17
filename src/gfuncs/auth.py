import json
import os
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

API_METDATA = {"gmail": {"version": "v1"}, "drive": {"version": "v3"}}
PATH_AUTH = Path(__file__).parent / "auth"
PATH_CREDS = PATH_AUTH / "credentials.json"
PATH_TOKEN = PATH_AUTH / "token.json"
PATH_USER = PATH_AUTH / "user.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.send",
]


def info() -> None:
    """Print info about the user."""
    print(f"Authentication info located at {PATH_AUTH}")
    print(f"{API_METDATA=}")
    print(f"{PATH_CREDS=}")
    print(f"{PATH_TOKEN=}")
    print(f"{PATH_USER=}")
    print(f"{SCOPES=}")


def service(api: str) -> Any:
    """Create a Google API service.

    Args:
        api (str): Name of API to create service for.

    Raises:
        NotImplementedError: If API is not supported.

    Returns:
        Any: Google API service.
    """
    if api not in API_METDATA:
        raise NotImplementedError(f"{api} API not supported")
    else:
        version = API_METDATA[api]["version"]

    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(PATH_TOKEN):
        creds = Credentials.from_authorized_user_file(PATH_TOKEN, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(PATH_CREDS, SCOPES)
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Credentials file not found at {PATH_AUTH}. See https://developers.google.com/workspace/guides/create-project for instructions on how to create a credentials file."
                )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(PATH_TOKEN, "w") as token:
            token.write(creds.to_json())

    # Generate and return service
    return build(api, version, credentials=creds, cache_discovery=False)


def username() -> str:
    """Get the username of the user.

    Returns:
        str: The username of the user.
    """
    with open(PATH_USER) as f:
        username = json.load(f)["username"]

    return username
