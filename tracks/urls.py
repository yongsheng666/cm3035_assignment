from django.urls import path
from . import views

urlpatterns = [
    # Core REST list/create (GET/POST)
    path("tracks/", views.TrackListCreateView.as_view(), name="api-track-list-create"),

    # Summary endpoints
    path("tracks/summary/top-artists/", views.top_artists, name="api-top-artists"),
    path("tracks/summary/releases-by-year/", views.releases_by_year, name="api-releases-by-year"),
    path("tracks/summary/top-genres/", views.top_genres, name="api-top-genres"),

    # New “complex” endpoints
    path("tracks/insights/clean-hits/", views.clean_hits, name="api-clean-hits"),
    path("tracks/insights/artist-albumtype-breakdown/", views.artist_albumtype_breakdown, name="api-artist-albumtype-breakdown"),
]
