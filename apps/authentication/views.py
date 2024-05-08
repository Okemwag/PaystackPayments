# views.py
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import OTP
from .serializers import OTPGenerateSerializer, OTPVerifySerializer
from random import randint

@api_view(['POST'])
def generate_otp(request):
    serializer = OTPGenerateSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        # Generate a random 6-digit OTP
        otp = ''.join([str(randint(0, 9)) for _ in range(6)])
        # Save the OTP to the database with an expiry time (e.g., 5 minutes from now)
        expiry_time = timezone.now() + timezone.timedelta(minutes=5)
        OTP.objects.update_or_create(
            phone_number=phone_number,
            defaults={'otp': otp, 'expiry_time': expiry_time}
        )
        
        return Response({'message': 'OTP generated successfully'}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp(request):
    serializer = OTPVerifySerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']
        # Retrieve the OTP object from the database
        otp_obj = get_object_or_404(OTP, phone_number=phone_number)
        # Check if the OTP is still valid and matches the one provided
        if otp_obj.is_valid() and otp_obj.otp == otp:
            
            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
