from twilio.rest import Client


def send_sms(to_phone, message):
    account_sid = 'AC8c2c76de2242051d425a909af44a84af'
    auth_token = 'AC8c2c76de2242051d425a909af44a84af:5de7fad157efaac3c6a6c9b0944bed14'
    from_phone = '+12403485067'

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
