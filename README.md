## A personal scheduling app with Google Calendar integration

This app is similar to Calendly but simpler and tailored for my personal needs. The problem with Calendly is that the free version only allows 1 event type. Well, **BookMe** allows multiple pre-defined event types.

**NOTE:** The app is currently a WIP. There will be bugs. This README will be updated as the app progresses in development.

## Pre-requisites

* A Google project with Calendar API enabled and an OAuth desktop Client ID. Make sure to download the JSON credentials of the client ID.
* In addition, register the application for the OAuth consent screen. The scope that needs to be added is `./auth/calendar`.

## Instructions for development

1. Create a `secrets` folder in the root directory.
2. Move the downloaded *credentials.json* file into the `secrets` folder.
3. Run `poetry run python manage.py tailwind start` to start the Tailwind hotloader.
4. Run `poetry run python manage.py runserver` to start the Django server.
