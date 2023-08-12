from django.contrib import admin
from sauces.models import Sauce, Source, Artist

# Register your models here.


class SauceAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "sauce_type", "source", "site_id")
    list_filter = (
        "sauce_type",
        "source",
    )


class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "website")


class ArtistAdmin(admin.ModelAdmin):
    list_display = ("names",)
    search_fields = ("names",)


admin.site.register(Sauce, SauceAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Artist, ArtistAdmin)
