from django.core.management.base import BaseCommand
from scheduler.lib.calendarauth import CalendarAuth


class Command(BaseCommand):
    help = "Manage token for Calendar API service."

    def add_arguments(self, parser):
        parser.add_argument("command", help="management command")

    def handle(self, *args, **options):
        auth = CalendarAuth()

        if options["command"] == "checktoken":
            if auth.is_valid:
                self.stdout.write("Token is valid.")
            else:
                self.stdout.write("Token is invalid.")
        if options["command"] == "refreshtoken":
            refreshed = auth.refresh_token()
            if refreshed:
                self.stdout.write("Token refreshed!")
        if options["command"] == "generatetoken":
            auth.generate_token()
            self.stdout.write("Token saved!")
