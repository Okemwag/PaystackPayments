import requests
from django.conf import settings

token = settings.PAYSTACK_SECRET


def initialize_transaction(email: str, amount: int, **kwargs):
    url = "https://api.paystack.co/transaction/initialize"
    data = {
        "email": email,
        "amount": f"{amount}"
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()


def verify_transaction(ref: str):
    url = f"https://api.paystack.co/transaction/verify/{ref}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()
