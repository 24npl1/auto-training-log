import smtplib
from email.mime.text import MIMEText

def send_email(subject, text_file, sender, recipients, password, links = None):
    """
    Sends an email using Gmail's SMTP server with the provided credentials.

    Arguments:
    subject -- a string representing the subject of the email
    text_file -- a string representing the path to a text file containing the email body
    sender -- a string representing the sender's email address
    recipients -- a list of strings representing the recipients' email addresses
    password -- a string representing the password for the sender's email account
    links -- an optional string representing additional links to include in the email body

    Returns:
    None
    """
    print("Emailing: " + (i + " " for i in recipients))
    with open(text_file,"r") as f:
        str_msg = f.read()
    if links:
        str_msg += "\n" + links
    msg = MIMEText(str_msg)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()
    print("Sent!")
