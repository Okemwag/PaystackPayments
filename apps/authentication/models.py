from django.db import models
from django.utils import timezone

class OTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    otp_hash = models.CharField(max_length=128)  
    expiry_time = models.DateTimeField()  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone_number

    def is_valid(self):
        """Check if the OTP is still valid."""
        return self.expiry_time > timezone.now()
