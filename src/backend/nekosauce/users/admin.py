from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from nekosauce.users.models import *


class UwUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("api_key", "donation", "donation_date")}),
    )


admin.site.register(User, UwUserAdmin)
