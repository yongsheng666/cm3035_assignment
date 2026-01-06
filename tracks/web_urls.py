from django.urls import path
from . import web_views

urlpatterns = [
    path("", web_views.TrackListView.as_view(), name="tracks-web-list"),
    path("new/", web_views.TrackCreateView.as_view(), name="tracks-web-create"),
    path("<int:pk>/", web_views.TrackDetailView.as_view(), name="tracks-web-detail"),
    path("<int:pk>/edit/", web_views.TrackUpdateView.as_view(), name="tracks-web-edit"),
    path("<int:pk>/delete/", web_views.TrackDeleteView.as_view(), name="tracks-web-delete"),
]
