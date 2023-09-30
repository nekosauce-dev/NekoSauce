from django.contrib import admin

from nekosauce.sauces.models import Sauce


@admin.register(Sauce)
class SauceAdmin(admin.ModelAdmin):
    list_display = ("id", "source_id", "height", "width")
    search_fields = ("id", "source_site_id", "source_id", "tags")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = [f.name for f in self.model._meta.get_fields()]
