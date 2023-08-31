from django.contrib import admin

from nekosauce.stats.models import *

# Register your models here.


class StatisticAdmin(admin.ModelAdmin):
    list_display = ("resource", "attribute", "value", "created_at")
    search_fields = ("resource", "attribute")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"


admin.site.register(Statistic, StatisticAdmin)
