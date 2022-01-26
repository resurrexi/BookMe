from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from scheduler.models import Event

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class EventPlanner:
    def __init__(self):
        self.token_file = settings.SECRETS_PATH / "token.json"
        self.credentials_file = settings.SECRETS_PATH / "credentials.json"

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

    def plan_event(self, guests, event, event_name):
        # first guest in the list should always be the app owner
        guests = [
            {
                "email": email,
                "responseStatus": "accepted" if idx == 0 else "needsAction",
            }
            for idx, email in enumerate(guests)
        ]

        service_body = {
            "summary": event_name,
            "start": {"dateTime": event.start_time},
            "end": {"dateTime": event.end_time},
            "description": event.description,
            "attendees": guests,
            "reminders": {"useDefault": True},
        }

        if event.location_type == Event.LocationType.GOOGLE_MEET:
            service_body["conferenceData"] = {
                "createRequest": {
                    "requestId": event.id,
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }

        service = self._authorize()

        return (
            service.events()
            .insert(
                calendarId="primary",
                sendNotifications=True,
                body=service_body,
                conferenceDataVersion=1,
            )
            .execute()
        )

    def get_events(self, time_lower, time_upper):
        service = self._authorize()
        results = []
        page_token = None

        # https://developers.google.com/calendar/api/v3/reference/events/list
        while True:
            events = (
                service.events()
                .list(
                    calendarId="primary",
                    pageToken=page_token,
                    timeMin=time_lower,
                    timeMax=time_upper,
                )
                .execute()
            )
            for event in events["items"]:
                results.append({"start": event["start"], "end": event["end"]})
            page_token = events.get("nextPageToken")
            if not page_token:
                break

        return results
