import logging
from rest_framework import serializers

from apps.payments.models import Payment, UserAccount
from apps.payments.services import initialize_transaction, verify_transaction

logger = logging.getLogger(__name__)


class CallbackSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=256)

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop("account")
        super().__init__(*args, **kwargs)

    def validate(self, data):
        super().validate(data)
        ref = data['reference']
        payments = self.account.payments.filter(reference=ref)
        if not payments:
            raise serializers.ValidationError(
                "Payment not found"
            )

        resp = verify_transaction(ref)
        if not resp.ok:
            raise serializers.ValidationError(
                "An error occurred while processing your request"
            )
        d = resp.json()
        if not d:
            logger.error(resp.text)
            raise serializers.ValidationError(
                "An error occurred while processing your request"
            )
        status: bool = f"{d.get("status")}" == "true"
        if not status:
            logger.error(d.get("message"))
            raise serializers.ValidationError(
                "An error occurred while processing your request"
            )
        self.payment = payments.first()
        return data

    def save(self, **kwargs):
        payment: Payment = self.payment
        payment.finalized = True
        payment.save()
        return payment


class PaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=10000)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def validate(self, data):
        super().validate(data)
        amount = data['amount']
        callback = self.context.get("callback")

        resp = initialize_transaction(
            email=self.user.email,
            amount=amount,
            callback=callback,
        )
        if not resp.ok:
            logger.error(resp.text)
            raise serializers.ValidationError(
                "An error occurred while processing your request"
            )

        resp_d = resp.json()
        d = resp_d.get("data")
        if not d:
            raise serializers.ValidationError(
                "An error occurred while processing your request"
            )
        authorization_url = d.get("authorization_url")
        ref = d.get("reference")

        data["authorization_url"] = authorization_url
        data["reference"] = ref

        return data

    def save(self, **kwargs):
        account: UserAccount = self.instance
        amount = self.validated_data['amount']
        ref = self.validated_data['reference']
        payment = Payment(
            account=account,
            amount=amount,
            reference=ref,
        )

        payment.save()
        return payment
