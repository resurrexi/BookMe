import smtplib
import pytz
import string
import os

from datetime import datetime, timedelta
from random import choice
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from pytz import timezone
from icalendar import Calendar, Event, vCalAddress, vText

# implementation credits
# https://stackoverflow.com/questions/57141694/why-encode-base64-give-me-typeerror-expected-bytes-like-object-not-nonetype/62255629#62255629
# will need to test


def generate_string(length):
    choices = string.ascii_lowercase + string.digits
    return ''.join(choice(choices) for i in range(length))


login = "yang.liquan87@gmail.com"
password = os.getenv("APP_PASSWORD")

# calendar props
prodid = "-//Pursuit of Zen//Book Me//EN"
version = "2.0"
calscale = "GREGORIAN"
method = "REQUEST"

# event props
utc = pytz.utc
requestor_tz = timezone("US/Eastern")
dtstart = requestor_tz.localize(datetime(2022, 1, 12, 12, 0, 0)).astimezone(utc)
dtend = dtstart + timedelta(minutes=30)
dtstamp = datetime.now(utc)
attendees = ["yang.liquan87@gmail.com", "tidus_the_chosen@hotmail.com", "2360953680@qq.com"]
organizer = "yang.liquan87@gmail.com"
summary = "Test Invitation"
description = "This is a test invitation.\n\nYou were identified as a test user."
location = ""
sequence = "0"
status = "CONFIRMED"
transparency = "OPAQUE"

# begin
cal = Calendar()
cal.add("PRODID", prodid)
cal.add("VERSION", version)
cal.add("CALSCALE", calscale)
cal.add("METHOD", method)

# generate event
event = Event()
event.add("DTSTART", dtstart)
event.add("DTEND", dtend)
event.add("DTSTAMP", dtstamp)
event_organizer = vCalAddress(f"mailto:{organizer}")
event_organizer.params["CN"] = vText(organizer)
event["ORGANIZER"] = event_organizer
event["UID"] = f"{generate_string(32)}@pursuitofzen.com"
for idx, attendee in enumerate(attendees):
    event_attendee = vCalAddress(f"mailto:{attendee}")
    event_attendee.params["CUTYPE"] = vText("INDIVIDUAL")
    event_attendee.params["ROLE"] = vText("REQ-PARTICIPANT")
    event_attendee.params["PARTSTAT"] = vText("ACCEPTED") if idx == 0 else vText("NEEDS-ACTION")
    event_attendee.params["RSVP"] = vText("TRUE")
    event_attendee.params["CN"] = vText(attendee)
    event_attendee.params["X-NUM-GUESTS"] = vText("0")
    event.add("ATTENDEE", event_attendee, encode=0)
event.add("CREATED", dtstamp)
event.add("DESCRIPTION", description)
event.add("LAST-MODIFIED", dtstamp)
event.add("LOCATION", location)
event.add("SEQUENCE", sequence)
event.add("STATUS", status)
event.add("SUMMARY", summary)
event.add("TRANSP", transparency)
cal.add_component(event)

# init email object
email_body = "Test email body"
email_body_bin = "Email body in binary"
msg = MIMEMultipart("mixed")
msg["Reply-To"] = organizer
msg["Date"] = formatdate(localtime=True)
msg["Subject"] = summary
msg["From"] = organizer
msg["To"] = ",".join(attendees)

email_part = MIMEText(email_body, "html", "UTF-8")
calendar_part = MIMEText(cal.to_ical().decode("utf-8"), 'calendar;method=REQUEST')

alternative_msg = MIMEMultipart("alternative")
msg.attach(alternative_msg)

cal_attach = MIMEApplication(cal.to_ical(), "ics")
cal_attach.add_header("Content-Type", "application/ics", name="invite.ics")
cal_attach.add_header("Content-Disposition", "attachment", filename="invite.ics")
cal_attach.add_header("Content-Transfer-Encoding", "base64")

email_attach = MIMEText("", "plain")
encoders.encode_base64(email_attach)
email_attach.add_header("Content-Transfer-Encoding", "")

alternative_msg.attach(email_part)
alternative_msg.attach(calendar_part)

mail_server = smtplib.SMTP("smtp.gmail.com", 587)
mail_server.ehlo()
mail_server.starttls()
mail_server.ehlo()
mail_server.login(login, password)
mail_server.sendmail(organizer, attendees, msg.as_string())
mail_server.close()
