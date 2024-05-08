from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from .models import Payment
from user.models import User
from .services import initialize_transaction, verify_transaction


@login_required
def deposit_cash(request):
    amount = request.POST.get("amount")
    user: User = request.user
    account = user.retrieve_account()
    payment = Payment(
        account=account,
        amount=amount,
    )
    response = initialize_transaction(user.email, amount)
    if not response.ok:
        payment.delete()
        return HttpResponse("An error occurred while processing your request")
    url = response["data"]["authorization_url"]
    ref = response["data"]["reference"]
    payment.reference = ref
    payment.save()
    return HttpResponseRedirect(url)
