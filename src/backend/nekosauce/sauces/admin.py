from django.contrib import admin

from nekosauce.sauces.models import (
    Sauce,
    Source,
    Hash
)


@admin.register(Sauce)
class SauceAdmin(admin.ModelAdmin):
    list_display = ("title", "height", "width")
    search_fields = ("title", "source__name", "tags")
    raw_id_fields = ("source", "hash",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = [f.name for f in self.model._meta.get_fields()]


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "api_docs", "enabled")
    list_filter = ("enabled",)
    search_fields = ("name", "website", "api_docs")


@admin.register(Hash)
class HashAdmin(admin.ModelAdmin):
    list_display = ("bits",)
    search_fields = ("bits",)
