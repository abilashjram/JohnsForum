import json
import requests
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email(receiver_email, subject, text):

    sender_email = os.getenv("MY_SENDER_EMAIL")

    api_key = os.getenv("SENDGRID_API_KEY")

    if sender_email and api_key:
        url = "https://api.sendgrid.com/v3/mail/send"

        data = {"personalizations": [{
                    "to": [{"email": receiver_email}],
                    "subject": subject
                }],

                "from": {"email": sender_email},

                "content": [{
                    "type": "text/plain",
                    "value": text
                }]
        }

        headers = {
            'authorization': "Bearer {0}".format(api_key),
            'content-type': "application/json"
        }

        response = requests.request("POST", url=url, data=json.dumps(data), headers=headers)

        print("Sent to SendGrid")
        print(response.text)
    else:
        print("No env vars or no email address")


def send_email_from_sendgridlib (receiver_email, subject, text):
    message = Mail(
        from_email='abilashjanakiraman@protonmail.com',
        to_emails=receiver_email,
        subject=subject,
        html_content=text)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)



