import os
import time
from mailjet_rest import Client
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

def send_email(recipient=None, max_retries=3, retry_delay=5):
    api_key    = os.getenv('MAILJET_API_KEY')
    secret_key = os.getenv('MAILJET_SECRET_KEY')
    sender     = os.getenv('SENDER_EMAIL')
    recipient  = recipient or os.getenv('RECIPIENT_EMAIL')

    if not all([api_key, secret_key, sender, recipient]):
        raise ValueError("MAILJET_API_KEY, MAILJET_SECRET_KEY, SENDER_EMAIL and RECIPIENT_EMAIL must be set in .env")

    html_path = os.path.join(OUTPUT_DIR, 'weekly_pulse.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    mailjet = Client(auth=(api_key, secret_key), version='v3.1')
    data = {
        'Messages': [{
            'From':     {'Email': sender, 'Name': 'ChatGPT Pulse'},
            'To':       [{'Email': recipient}],
            'Subject':  'ChatGPT India — Weekly Review Pulse',
            'HTMLPart': html_content,
        }]
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            result = mailjet.send.create(data=data)
            if result.status_code == 200:
                print(f"Email sent to: {recipient}")
                return
            raise RuntimeError(f"Mailjet returned {result.status_code}: {result.json()}")
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                wait = retry_delay * attempt
                print(f"Attempt {attempt} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"Attempt {attempt} failed: {e}.")

    raise RuntimeError(f"Failed to send email after {max_retries} attempts: {last_error}")

if __name__ == '__main__':
    send_email()
