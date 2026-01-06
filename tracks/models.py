from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Track(models.Model):
    track_id = models.CharField(max_length=80, unique=True)

    track_name = models.CharField(max_length=300)
    track_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    # Spotify popularity is 0–100
    track_popularity = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    explicit = models.BooleanField(default=False)

    artist_name = models.CharField(max_length=300)

    # Spotify popularity is 0–100
    artist_popularity = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # followers should never be negative
    artist_followers = models.BigIntegerField(
        validators=[MinValueValidator(0)]
    )

    artist_genres = models.TextField(blank=True, null=True)

    album_id = models.CharField(max_length=80)
    album_name = models.CharField(max_length=300)

    album_release_date = models.DateField()

    album_total_tracks = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    # constrain to known values if your dataset uses these; otherwise keep as CharField only
    ALBUM_TYPES = (
        ("album", "album"),
        ("single", "single"),
        ("compilation", "compilation"),
    )
    album_type = models.CharField(max_length=50, choices=ALBUM_TYPES)

    # must be positive and realistic (minutes)
    track_duration_min = models.FloatField(
        validators=[MinValueValidator(0.01), MaxValueValidator(600.0)]
    )

    def clean(self):
        errors = {}

        # prevent accidental future release dates
        if self.album_release_date and self.album_release_date > timezone.now().date():
            errors["album_release_date"] = "Release date cannot be in the future."

        # duration sanity: seconds mistaken as minutes becomes huge; cap already helps,
        # but also catch NaN / inf values if they ever appear
        if self.track_duration_min is not None:
            if self.track_duration_min != self.track_duration_min:  # NaN check
                errors["track_duration_min"] = "Duration is invalid (NaN)."

        # genre length sanity (avoid extreme garbage input)
        if self.artist_genres and len(self.artist_genres) > 2000:
            errors["artist_genres"] = "Genres text is too long."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.track_name} — {self.artist_name}"
