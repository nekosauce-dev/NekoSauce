from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from nekosauce.users.models import *

# Register your models here.


admin.site.register(User, UserAdmin)
