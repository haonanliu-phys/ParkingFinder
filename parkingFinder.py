import requests
import hashlib
import os
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def get_list_from_txt(filename: str) -> list[str]: 

    try:
        with open(filename, 'r') as file:
            email_list = []
            for line in file:
                stripped_line = line.strip()
                # Skip lines that are empty or start with "# "
                if stripped_line.startswith('#'):
                    continue
                if stripped_line:
                    email_list.append(stripped_line)
            return email_list
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return []

def send_email(sender: str, sender_key: str, receivers: list[str], subject: str, body: str) -> None:

    for receiver in receivers:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # For gmail we need to use the app password
        server.login(sender, sender_key)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()


def send_no_update_email(sender: str, sender_key: str, receivers: list[str]) -> None:

    subject = 'Copper Parking Not Updated'
    body = f'The Copper parking website has NOT been updated on {today}.'
    send_email(sender, sender_key, receivers, subject, body)
    

def send_update_email(sender: str, sender_key: str, receivers: list[str]) -> None:

    subject = 'Copper Parking Updated'
    body = f'The Copper parking website has been updated on {today}.'
    send_email(sender, sender_key, receivers, subject, body)


def check_website_update(url_old, url_new, hash_file_path):

    try:
        response = requests.get(url_old)
        response.raise_for_status()  # Raises stored HTTPError, if one occurred.
    except requests.exceptions.RequestException as err:
        try:
            response = requests.get(url_new)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print(f"Both urls are invalid.")
            return False
        
    current_hash = hashlib.sha256(response.text.encode('utf-8')).hexdigest()

    if os.path.exists(hash_file_path):
        with open(hash_file_path, 'r') as file:
            old_hash = file.read()
    else:
        old_hash = None

    with open(hash_file_path, 'w') as file:
        file.write(current_hash)

    if old_hash is not None and current_hash != old_hash:
        return True

    return False

# Usage
url_old = 'https://www.coppercolorado.com/tickets-passes/season-passes/parking-pass-24-25-standalone'
url_new = 'https://www.coppercolorado.com/plan-your-trip/season-passes/parking-pass-25-26-standalone'
hash_file_path = 'website_hash.txt' 

today = datetime.date.today()
receivers = get_list_from_txt('parameters/receivers.txt') 
sender = get_list_from_txt('parameters/sender.txt')[0] 
sender_key = get_list_from_txt('parameters/sender_key.txt')[0]

if check_website_update(url_old, url_new, hash_file_path):
    print(f'Website has been updated on {today}.')
    send_update_email(sender, sender_key, receivers)
else:
    print(f'No updates on the website on {today}.')
    send_no_update_email(sender, sender_key, receivers)