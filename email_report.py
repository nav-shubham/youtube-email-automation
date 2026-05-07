import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import pandas as pd
import pytz
import re
from dotenv import load_dotenv
import os

load_dotenv()


def get_email_report():
    accounts = [
        {
            "username": os.getenv("EMAIL_1"),
            "password": os.getenv("EMAIL_1_PASSWORD")
        },
        {
            "username": os.getenv("EMAIL_2"),
            "password": os.getenv("EMAIL_2_PASSWORD")
        }
    ]

    ist = pytz.timezone('Asia/Kolkata')
    all_data = []

    for acc in accounts:
        username = acc["username"]
        password = acc["password"]

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")

        date_48hrs = (datetime.now() - timedelta(hours=48)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SINCE "{date_48hrs}")')
        email_ids = messages[0].split()

        for e_id in email_ids:
            res, msg_data = mail.fetch(e_id, "(RFC822)")

            for response in msg_data:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    subject = re.sub(r'[<>]', '', subject)
                    from_ = msg.get("From")

                    date_ = msg.get("Date")
                    email_date = email.utils.parsedate_to_datetime(date_)
                    email_date_ist = email_date.astimezone(ist)

                    date_only = email_date_ist.strftime("%Y-%m-%d")
                    time_only = email_date_ist.strftime("%H:%M:%S")

                    gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{e_id.decode()}"

                    all_data.append([
                        username,
                        date_only,
                        time_only,
                        from_,
                        subject,
                        gmail_link
                    ])

        mail.logout()

    df = pd.DataFrame(all_data, columns=[
        "Account",
        "Date (IST)",
        "Time (IST)",
        "From",
        "Subject",
        "Open Email"
    ])

    return df


def main():
    df = get_email_report()
    df.to_excel("Email_Report.xlsx", index=False)
    print("Email_Report.xlsx created")


if __name__ == "__main__":
    main()
