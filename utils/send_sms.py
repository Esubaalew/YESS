from twilio.rest import Client
from decouple import config


def send_sms(to_phone, message):
    account_sid = config('TWILIO_ACCOUNT_SID')
    auth_token = config('TWILIO_AUTH_TOKEN')
    from_phone = config('TWILIO_PHONE_NUMBER')

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        print("SMS sent successfully.")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
