import requests
import json
from django.shortcuts import get_object_or_404
from members.models import PasswordResetToken
from django.utils import timezone
import os 

def send_sms(phone_number, message):
    url = "https://sms.textsms.co.ke/api/services/sendsms"
    payload = {
        "mobile": f'+254{phone_number}',
        "response_type": "json",
        "partnerID": os.environ.get('partnerID'),
        "shortcode": os.environ.get('shortcode'),
        'apikey': os.environ.get('apikey'),
        "message": message
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.text

def verify_verification_code(user, verification_code):
    print(verification_code)
    print(user)
    reset_token = get_object_or_404(PasswordResetToken, user=user)
    print(reset_token)
    if reset_token.verification_code == verification_code:
        # Check if the token has expired (e.g., within 5 minutes)
        if timezone.now() - reset_token.created_at <= timezone.timedelta(minutes=5):
            return user
    return None