from django.contrib import admin

from nekosauce.sauces.models import Sauce
from nekosauce.sauces.utils.registry import registry


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
    list_display = ("id", "source_id", "source_site_id", "status", "created_at")
    search_fields = ("id", "source_site_id", "source_id", "tags")
    list_filter = (SourceListFilter, "status")
    ordering = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = [f.name for f in self.model._meta.get_fields()]
