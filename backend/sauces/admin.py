from django.contrib import admin

from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)

from sauces.models import (
    Sauce,
    ArtSauce,
    MangaSauce,
    AnimeSauce,
    Source,
    Entity,
    Artist,
    Uploader,
    Hash,
)

# Register your models here.


class EntityChildAdmin(PolymorphicChildModelAdmin):
    base_class = Entity
    base_list_display = ("names", "tags")


class SauceChildAdmin(PolymorphicChildModelAdmin):
    base_class = Sauce
    autocomplete_fields = ("uploaders", "hashes")
    list_display = ("title", "source", "downloaded", "tags")


@admin.register(Sauce)
class SauceParentAdmin(PolymorphicParentModelAdmin):
    base_class = Sauce
    child_models = (ArtSauce, MangaSauce, AnimeSauce)
    list_display = ("title", "source", "downloaded", "tags")
    list_filter = (PolymorphicChildModelFilter, "downloaded")


@admin.register(ArtSauce)
class ArtSauceAdmin(SauceChildAdmin):
    base_class = ArtSauce
    raw_id_fields = ("artist",)
    list_display = ("title", "source", "downloaded", "artist", "tags")


@admin.register(AnimeSauce)
class AnimeSauceAdmin(SauceChildAdmin):
    base_class = AnimeSauce


@admin.register(MangaSauce)
class MangaSauceAdmin(SauceChildAdmin):
    base_class = MangaSauce
    raw_id_fields = ("artist",)
    list_display = ("title", "source", "downloaded", "artist", "tags")


@admin.register(Entity)
class EntityParentAdmin(PolymorphicParentModelAdmin):
    base_class = Entity
    child_models = (Artist, Uploader)
    list_filter = (PolymorphicChildModelFilter,)


@admin.register(Uploader)
class UploaderAdmin(EntityChildAdmin):
    base_class = Uploader
    search_fields = ("names",)


@admin.register(Artist)
class ArtistAdmin(EntityChildAdmin):
    base_class = Artist
    search_fields = ("names",)
    raw_id_fields = ("direct_uploader",)


@admin.register(Hash)
class HashAdmin(admin.ModelAdmin):
    list_display = ("bits",)
    search_fields = ("bits", "sauces__title")


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "api_docs")
    search_fields = ("name",)
