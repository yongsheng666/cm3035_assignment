from django import forms
from .models import Track


class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = [
            "track_id",
            "track_name",
            "track_number",
            "track_popularity",
            "explicit",
            "artist_name",
            "artist_popularity",
            "artist_followers",
            "artist_genres",
            "album_id",
            "album_name",
            "album_release_date",
            "album_total_tracks",
            "album_type",
            "track_duration_min",
        ]
        widgets = {
            "album_release_date": forms.DateInput(attrs={"type": "date"}),
            "artist_genres": forms.Textarea(attrs={"rows": 2}),
        }
