from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()



class Gender(models.TextChoices):
    MALE = "Male", _("Male")
    FEMALE = "Female", _("Female")
    OTHER = "Other", _("Other")


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", related_query_name="profile", primary_key=True, unique=True, default=1
    )
    phone_number = PhoneNumberField( unique=True)
           
    profile_photo = models.ImageField(
        verbose_name=_("Profile Photo"), upload_to="profiles/", blank=True, null=True
    )
    gender = models.CharField(
        verbose_name=_("Gender"),
        choices=Gender.choices,
        default=Gender.OTHER,
        max_length=20,
    )
    
    city = models.CharField(
        verbose_name=_("City"),
        max_length=180,
        default="Nairobi",
        blank=False,
        null=False,
    )
    
    
    def __str__(self):
        return f"{self.user.username}'s profile"
