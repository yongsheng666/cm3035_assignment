from collections import Counter
from django.db.models import Count, Avg, Max, Min
from django.db.models.functions import ExtractYear
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Track
from .serializers import (
    TrackSerializer,
    TopArtistSummarySerializer,
    ReleasesByYearSerializer,
    GenreCountSerializer,
    CleanHitsSerializer,
    ArtistAlbumTypeBreakdownSerializer,
)


class TrackListCreateView(generics.ListCreateAPIView):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer

    # DRF search + ordering (demonstrates DRF knowledge)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["track_name", "artist_name", "album_name", "artist_genres"]
    ordering_fields = ["track_popularity", "album_release_date", "artist_followers", "track_duration_min"]
    ordering = ["-track_popularity"]

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params

        artist = p.get("artist")
        album_type = p.get("album_type")
        genre = p.get("genre")
        explicit = p.get("explicit")
        min_pop = p.get("min_popularity")
        min_followers = p.get("min_followers")
        year = p.get("year")
        from_date = p.get("from_date")
        to_date = p.get("to_date")

        if artist:
            qs = qs.filter(artist_name__icontains=artist)

        if album_type:
            qs = qs.filter(album_type__iexact=album_type)

        if genre:
            qs = qs.filter(artist_genres__icontains=genre)

        if explicit is not None:
            if explicit.lower() == "true":
                qs = qs.filter(explicit=True)
            elif explicit.lower() == "false":
                qs = qs.filter(explicit=False)

        if min_pop:
            qs = qs.filter(track_popularity__gte=int(min_pop))

        if min_followers:
            qs = qs.filter(artist_followers__gte=int(min_followers))

        if year:
            qs = qs.filter(album_release_date__year=int(year))

        if from_date:
            qs = qs.filter(album_release_date__gte=from_date)
        if to_date:
            qs = qs.filter(album_release_date__lte=to_date)

        return qs


@api_view(["GET"])
def top_artists(request):
    rows = list(
        Track.objects.values("artist_name")
        .annotate(
            track_count=Count("id"),
            avg_track_popularity=Avg("track_popularity"),
            max_track_popularity=Max("track_popularity"),
            followers=Avg("artist_followers"),
        )
        .order_by("-track_count", "-followers")[:20]
    )
    return Response(TopArtistSummarySerializer(rows, many=True).data)


@api_view(["GET"])
def releases_by_year(request):
    rows = list(
        Track.objects.annotate(year=ExtractYear("album_release_date"))
        .values("year")
        .annotate(
            track_count=Count("id"),
            avg_track_popularity=Avg("track_popularity"),
        )
        .order_by("year")
    )

    # explicit_count computed in Python (fast enough for <10k rows, SQLite-safe)
    explicit_counts = {}
    for r in Track.objects.annotate(year=ExtractYear("album_release_date")).values("year", "explicit"):
        y = r["year"]
        explicit_counts.setdefault(y, 0)
        if r["explicit"]:
            explicit_counts[y] += 1

    for row in rows:
        row["explicit_count"] = explicit_counts.get(row["year"], 0)

    return Response(ReleasesByYearSerializer(rows, many=True).data)


@api_view(["GET"])
def top_genres(request):
    top_n = int(request.query_params.get("top", 20))
    genres = []

    for g in Track.objects.values_list("artist_genres", flat=True):
        if g:
            genres.extend([x.strip().lower() for x in g.split(",") if x.strip()])

    counts = Counter(genres).most_common(top_n)
    rows = [{"genre": k, "count": v} for k, v in counts]
    return Response(GenreCountSerializer(rows, many=True).data)


@api_view(["GET"])
def clean_hits(request):
    """
    "Interesting" endpoint similar to the coursework example:
    High-popularity, non-explicit tracks with optional genre + year range + album type.
    """
    p = request.query_params
    min_popularity = int(p.get("min_popularity", 70))
    genre = (p.get("genre") or "").strip()
    year_from = p.get("year_from")
    year_to = p.get("year_to")
    album_type = (p.get("album_type") or "").strip()

    qs = Track.objects.filter(explicit=False, track_popularity__gte=min_popularity)

    if genre:
        qs = qs.filter(artist_genres__icontains=genre)
    if album_type:
        qs = qs.filter(album_type__iexact=album_type)
    if year_from:
        qs = qs.filter(album_release_date__year__gte=int(year_from))
    if year_to:
        qs = qs.filter(album_release_date__year__lte=int(year_to))

    summary = qs.aggregate(
        results=Count("id"),
        avg_popularity=Avg("track_popularity"),
        max_popularity=Max("track_popularity"),
        min_duration=Min("track_duration_min"),
        max_duration=Max("track_duration_min"),
    )

    top_tracks = qs.order_by("-track_popularity", "-artist_followers")[:25]

    payload = {
        "filters": {
            "min_popularity": min_popularity,
            "genre": genre or None,
            "year_from": int(year_from) if year_from else None,
            "year_to": int(year_to) if year_to else None,
            "album_type": album_type or None,
        },
        "summary": summary,
        "top_tracks": TrackSerializer(top_tracks, many=True).data,
    }
    return Response(CleanHitsSerializer(payload).data)


@api_view(["GET"])
def artist_albumtype_breakdown(request):
    artist = (request.query_params.get("artist") or "").strip()
    if not artist:
        return Response({"error": "Missing required param: artist"}, status=400)

    rows = list(
        Track.objects.filter(artist_name__icontains=artist)
        .values("artist_name", "album_type")
        .annotate(track_count=Count("id"), avg_track_popularity=Avg("track_popularity"))
        .order_by("artist_name", "album_type")
    )
    return Response(ArtistAlbumTypeBreakdownSerializer(rows, many=True).data)
