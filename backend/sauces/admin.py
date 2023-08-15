from django.contrib import admin

from sauces.models import (
    Sauce,
    Source,
    Hash,
)

# Register your models here.


@admin.register(Sauce)
class SauceAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "downloaded", "height", "width")
    list_filter = ("downloaded", "source")
    search_fields = ("title", "source")
    autocomplete_fields = ["hashes"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = [f.name for f in self.model._meta.get_fields()]


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "api_docs")


@admin.register(Hash)
class HashAdmin(admin.ModelAdmin):
    list_display = ("bits", "method")
    list_filter = ("method",)
    search_fields = ("bits",)
