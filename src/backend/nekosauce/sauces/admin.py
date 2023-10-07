from django.contrib import admin

from nekosauce.sauces.models import Sauce
from nekosauce.sauces.utils.registry import registry


class ProcessedSauceListFilter(admin.SimpleListFilter):
    title = "Processed"
    parameter_name = "processed"

    def lookups(self, request, model_admin):
        return (
            ("1", "Completely processed"),
            ("2", "Only wavelet hash"),
            ("3", "Only sha512 hash"),
            ("4", "Not processed"),
        )

    def queryset(self, request, queryset):
        return (
            queryset.filter(
                hash__isnull=self.value() in ["3", "4"],
                sha512__isnull=self.value() in ["2", "4"],
            )
            if self.value() is not None
            else queryset
        )


class SourceListFilter(admin.SimpleListFilter):
    title = "Source"
    parameter_name = "source"

    def lookups(self, request, model_admin):
        return [(source["id"], source["name"]) for source in registry["sources"]]

    def queryset(self, request, queryset):
        return (
            queryset.filter(source_id=self.value())
            if self.value() is not None
            else queryset
        )


@admin.register(Sauce)
class SauceAdmin(admin.ModelAdmin):
    list_display = ("id", "source_id", "source_site_id", "created_at")
    search_fields = ("id", "source_site_id", "source_id", "tags")
    list_filter = (SourceListFilter, ProcessedSauceListFilter)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = [f.name for f in self.model._meta.get_fields()]
