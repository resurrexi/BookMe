from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from uuid import uuid4
from datetime import datetime, timedelta

SECRETS_PATH = Path('./secrets')
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class EventPlanner:
    def __init__(self, guests, schedule):
        self.token_file = SECRETS_PATH / 'token.json'
        self.credentials_file = SECRETS_PATH / 'credentials.json'
        guests = [{"email": email} for email in guests]
        service = self._authorize()
        self.event_states = self._plan_event(guests, schedule, service)

    def _authorize(self):
        creds = None

        if self.token_file.exists():
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        calendar_service = build("calendar", "v3", credentials=creds)

        return calendar_service

    def _plan_event(self, attendees, event_time, service):
        event = {
            "summary": "test_meeting",
            "start": {
                "dateTime": event_time["start"]
            },
            "end": {
                "dateTime": event_time["end"]
            },
            "attendees": attendees,
            "conferenceData": {
                "createRequest": {
                    "requestId": uuid4().hex,
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    }
                }
            },
            "reminders": {
                "useDefault": True
            }
        }

        event = service.events() \
            .insert(
                calendarId="primary",
                sendNotifications=True,
                body=event,
                conferenceDataVersion=1
            ) \
            .execute()

        return event

if __name__ == "__main__":
    start = datetime.utcnow() + timedelta(hours=1)
    end = datetime.utcnow() + timedelta(hours=2)

    plan = EventPlanner(
        ["yang.liquan87@gmail.com", "tidus_the_chosen@hotmail.com"],
        {
            "start": start.isoformat() + 'Z',
            "end": end.isoformat() + 'Z',
        }
    )

    print(plan.event_states)
