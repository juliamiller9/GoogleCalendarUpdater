import imaplib
import email
import os
import schedule
import time
import yaml

#Account info
info = yaml.load(open('user:creds.yml'))
username = info['user']['email']
password = info['user']['password']
imap_url = "outlook.office365.com" #imap-mail.outlook.com

#Download attachment from email
def download_schedule():
    # Connect to email server and log in
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(username, password)
    mail.select("inbox")

    # Search for emails with attachments
    typ, msgs = mail.search(None, 'has', 'attachment')

    for num in msgs[0].split():
        # Get email message
        typ, data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])

        # Download attachments
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()

            if bool(filename):
                filepath = os.path.join('./attachments', filename)
                if not os.path.isfile(filepath):
                    fp = open(filepath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()

    # Disconnect from email server
    mail.close()
    mail.logout()

#Run script each time new schedule comes in
schedule.every().day.at("6:20").do(download_schedule())
schedule.every().day.at("18:20").do(download_schedule())

# Run script indefinitely
while True:
    schedule.run_pending()
    time.sleep(1)
