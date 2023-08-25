from django.contrib import admin

from nekosauce.sauces.models import (
    Sauce,
    Source,
    Hash8Bits,
    Hash16Bits,
    Hash32Bits,
    Hash64Bits,
)


@admin.register(Sauce)
class SauceAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "downloaded", "height", "width")
    list_select_related = ("source",)
    list_filter = ("downloaded", "source")
    search_fields = ("title", "source__name")
    date_hierarchy = "created_at"
    autocomplete_fields = ("hashes_8bits", "hashes_16bits", "hashes_32bits", "hashes_64bits",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = [f.name for f in self.model._meta.get_fields()]


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "api_docs")


class HashAdmin(admin.ModelAdmin):
    list_display = ("bits", "algorithm")
    list_filter = ("algorithm",)
    search_fields = ("bits",)


admin.site.register(Hash8Bits, HashAdmin)
admin.site.register(Hash16Bits, HashAdmin)
admin.site.register(Hash32Bits, HashAdmin)
admin.site.register(Hash64Bits, HashAdmin)
