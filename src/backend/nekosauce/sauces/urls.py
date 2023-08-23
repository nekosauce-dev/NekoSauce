from django.urls import path

from nekosauce.sauces.views import SearchView


urlpatterns = [
    path('search', SearchView.as_view(), name="search"),
]
