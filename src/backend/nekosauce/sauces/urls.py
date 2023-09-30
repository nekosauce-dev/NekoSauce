from django.urls import path

from nekosauce.sauces.views import SearchView, SourceView


urlpatterns = [
    path("search", SearchView.as_view(), name="search"),
    path("sources", SourceView.as_view(), name="sources"),
]
