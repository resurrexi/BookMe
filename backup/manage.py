import argparse
from bookme.lib.auth import CalendarAuth

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="management command")
    args = parser.parse_args()

    # create CalendarAuth instance
    auth = CalendarAuth()

    if args.command == "checktoken":
        print(auth.is_valid)
    if args.command == "refreshtoken":
        refreshed = auth.refresh_token()
        if refreshed:
            print("Token is refreshed")
    if args.command == "generatetoken":
        auth.generate_token()
        print("Token has been saved")
