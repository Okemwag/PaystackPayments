from django.shortcuts import reverse
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.payments.serializers import CallbackSerializer, PaymentSerializer
from .models import UserAccount
from user.models import User


class CheckoutAPIView(APIView):
    """
    User is authenticated
    Retirieve email/phone from user
    Amount from client
    Build request body including callback
        - User metadata
        - Auth Bearer <key>
    Send it to paystack
        Paystack returns response with checkout_url
        Paystach triggers stk push on customer phone
    User pays or not pays
    Paystack redirects user to callback url
    Goto callback view
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        data = request.POST.dict() or request.data
        user: User = request.user
        account: UserAccount = user.account

        callback = request.build_absolute_uri(reverse('payments:callback'))
        serializer = PaymentSerializer(
            instance=account,
            data=data,
            user=user,
            context={"callback": callback}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        url = serializer.validated_data['authorization_url']
        return HttpResponseRedirect(url)


class CallbackAPIView(APIView):
    """
    Paystack redirects user to this view
    While appending query params including reference
    Retrieve reference
    Validate reference then verify transaction with paystack
    If transaction is successful
        - Update payment status to finalized
        - Send email to user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        data = request.GET.dict() or request.data

        user: User = request.user
        account: UserAccount = user.account
        serializer = CallbackSerializer(
            data=data,
            account=account,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
