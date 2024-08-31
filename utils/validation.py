# utils/validation.py
import re
import phonenumbers


# Name validation
def is_valid_name(name):
    """Check if the name is at least 3 characters long and contains only letters."""
    if 3 <= len(name) <= 50 and name.isalpha():
        return True
    return False


# Email validation
def is_valid_email(email):
    """Check if the email is in a valid format."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


# Phone number validation
def is_valid_phone(phone):
    """Check if the phone number is valid, including country code."""
    try:
        parsed_phone = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed_phone)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False


# Needs validation
def is_valid_needs(needs):
    """Check if the needs field contains only textual input."""
    # Ensure the needs field is non-empty and contains only letters and spaces
    if len(needs) > 0 and re.match(r'^[a-zA-Z\s]+$', needs):
        return True
    return False
