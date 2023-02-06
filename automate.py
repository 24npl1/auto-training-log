from sheets_upload import upload_csv
from strava_to_csv import generate_csv
from auto_mail import send_email
from datetime import datetime

def main():
    client_id = 'xxxxxx'
    client_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    csv_name = f"week_ending_{datetime.today().strftime('%Y-%m-%d')}"
    target_name = "Weekly-Training-Log"
    generate_csv(client_id, client_secret, period = 7, filename = csv_name)
    upload_csv("./activities/" + csv_name, target_name)
    sheets_link = "LINK_TO_TARGET_SHEET"


    sender = "xxxx@gmail.com"
    filename = "./training_notes/xxxxx.txt"
    recipients = ["xxxxx@gmail.edu", "zzzzzz@gmail.edu"]
    password = "GMAIL_APP_PASSWORD"
    send_email(csv_name, filename, sender, recipients, password, links = sheets_link)


if __name__ == "__main__":
    main()