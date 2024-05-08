from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "gender", "phone_number", "city"]
    list_filter = ["gender","city"]
    list_display_links = ["user"]


admin.site.register(Profile, ProfileAdmin)
