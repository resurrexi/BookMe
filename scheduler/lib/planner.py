from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from uuid import uuid4
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class EventPlanner:
    def __init__(self, guests, event):
        # event is dictionary with keys `id`, `start`, `end`, `type`, `name`, `description`
        self.token_file = settings.SECRETS_PATH / "token.json"
        self.credentials_file = settings.SECRETS_PATH / "credentials.json"
        guests = [
            {
                "email": email,
                "responseStatus": "accepted" if idx == 0 else "needsAction",
            }
            for idx, email in enumerate(guests)
        ]
        service = self._authorize()
        self.event_states = self._plan_event(guests, event, service)

    def _authorize(self):
        creds = None

        if self.token_file.exists():
            creds = Credentials.from_authorized_user_file(
                self.token_file, SCOPES
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # save credentials for next run
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())

        calendar_service = build("calendar", "v3", credentials=creds)

        return calendar_service

    def _plan_event(self, attendees, event, service):
        new_event = {
            "summary": event["name"],
            "start": {"dateTime": event["start"]},
            "end": {"dateTime": event["end"]},
            "description": event["description"],
            "attendees": attendees,
            "reminders": {"useDefault": True},
        }

        if event["type"] == "gmeet":
            new_event["conferenceData"] = {
                "createRequest": {
                    "requestId": event["id"],
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }

        return (
            service.events()
            .insert(
                calendarId="primary",
                sendNotifications=True,
                body=new_event,
                conferenceDataVersion=1,
            )
            .execute()
        )


if __name__ == "__main__":
    start = datetime.utcnow() + timedelta(hours=1)
    end = datetime.utcnow() + timedelta(hours=2)

    plan = EventPlanner(
        ["yang.liquan87@gmail.com", "lyang@hush.com", "thedevhiro@gmail.com"],
        {
            "start": start.isoformat() + "Z",
            "end": end.isoformat() + "Z",
        },
    )

    print(plan.event_states)
