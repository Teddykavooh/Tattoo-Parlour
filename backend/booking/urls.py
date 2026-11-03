from django.urls import path

from .views import (
    ArtistListView,
    ServiceListView,
)

urlpatterns = [
    path(
        "artists/",
        ArtistListView.as_view(),
        name="artist-list"
    ),
    path(
        "services/",
        ServiceListView.as_view(),
        name="service-list"
    ),
]