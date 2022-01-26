from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarAuth:
    def __init__(self):
        self._token_file = settings.SECRETS_PATH / "token.json"
        self._credentials_file = settings.SECRETS_PATH / "credentials.json"
        self.creds = None

        # load credentials
        if self._token_file.exists():
            self.creds = Credentials.from_authorized_user_file(
                self._token_file, SCOPES
            )

    @property
    def is_valid(self):
        if not self.creds or not self.creds.valid:
            if not (
                self.creds and self.creds.expired and self.creds.refresh_token
            ):
                return False
        return True

    def refresh_token(self):
        if self.creds and self.creds.refresh_token:
            self.creds.refresh(Request())
            return self.creds
        raise ValueError("Unable to refresh token")

    def generate_token(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            self._credentials_file, SCOPES
        )
        self.creds = flow.run_console()

        # persist token
        with open(self._token_file, "w") as token:
            token.write(self.creds.to_json())
