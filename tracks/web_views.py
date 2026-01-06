from django.db.models import Q, Count, Avg
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from collections import Counter
from .models import Track
from .forms import TrackForm


class TrackListView(ListView):
    model = Track
    template_name = "tracks/track_list.html"
    context_object_name = "tracks"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.GET

        # Search
        q = p.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(track_name__icontains=q)
                | Q(artist_name__icontains=q)
                | Q(album_name__icontains=q)
                | Q(artist_genres__icontains=q)
            )

        # Filters
        album_type = p.get("album_type", "").strip()
        if album_type:
            qs = qs.filter(album_type__iexact=album_type)

        explicit = p.get("explicit", "").strip().lower()
        if explicit == "true":
            qs = qs.filter(explicit=True)
        elif explicit == "false":
            qs = qs.filter(explicit=False)

        min_pop = p.get("min_popularity", "").strip()
        if min_pop:
            qs = qs.filter(track_popularity__gte=int(min_pop))

        year = p.get("year", "").strip()
        if year:
            qs = qs.filter(album_release_date__year=int(year))

        artist = p.get("artist", "").strip()
        if artist:
            qs = qs.filter(artist_name__icontains=artist)

        genre = p.get("genre", "").strip()
        if genre:
            qs = qs.filter(artist_genres__icontains=genre)
        
        return qs


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Dropdown options
        ctx["album_types"] = (
            Track.objects.values_list("album_type", flat=True).distinct().order_by("album_type")
        )
        ctx["years"] = (
            Track.objects.values_list("album_release_date__year", flat=True)
            .distinct()
            .order_by("-album_release_date__year")
        )

        # Preserve filters across pagination (except page)
        params = self.request.GET.copy()
        if "page" in params:
            params.pop("page")
        ctx["querystring"] = params.urlencode()

        # -----------------------
        # Insights for UI (NOT API)
        # -----------------------

        # 1) Top artists (by count, with avg popularity)
        ctx["top_artists_ui"] = list(
            Track.objects.values("artist_name")
            .annotate(track_count=Count("id"), avg_popularity=Avg("track_popularity"))
            .order_by("-track_count")[:8]
        )

        # 2) Top genres (parse text field)
        genres = []
        for g in Track.objects.exclude(artist_genres__isnull=True).exclude(artist_genres="").values_list("artist_genres", flat=True):
            genres.extend([x.strip().lower() for x in g.split(",") if x.strip()])
        ctx["top_genres_ui"] = Counter(genres).most_common(10)

        # 3) “Clean hits” quick stats (non-explicit, high popularity)
        # These match your “interesting query” logic, but displayed as UI summary.
        clean_min_pop = 80
        clean_qs = Track.objects.filter(explicit=False, track_popularity__gte=clean_min_pop)
        ctx["clean_hits_ui"] = {
            "min_popularity": clean_min_pop,
            "count": clean_qs.count(),
            "avg_popularity": clean_qs.aggregate(avg=Avg("track_popularity"))["avg"],
        }

        # Artist dropdown (top N to keep UI fast)
        ctx["artists"] = (
            Track.objects.values_list("artist_name", flat=True)
            .distinct()
            .order_by("artist_name")[:300]
        )

        # Genre dropdown (parse comma-separated genres, unique + sorted)
        genres = set()
        for g in (
            Track.objects.exclude(artist_genres__isnull=True)
            .exclude(artist_genres="")
            .values_list("artist_genres", flat=True)
        ):
            for x in g.split(","):
                x = x.strip().lower()
                if x:
                    genres.add(x)

        ctx["genres"] = sorted(genres)

        return ctx


class TrackDetailView(DetailView):
    model = Track
    template_name = "tracks/track_detail.html"
    context_object_name = "track"


class TrackCreateView(CreateView):
    model = Track
    form_class = TrackForm
    template_name = "tracks/track_form.html"
    success_url = reverse_lazy("tracks-web-list")


class TrackUpdateView(UpdateView):
    model = Track
    form_class = TrackForm
    template_name = "tracks/track_form.html"
    success_url = reverse_lazy("tracks-web-list")


class TrackDeleteView(DeleteView):
    model = Track
    template_name = "tracks/track_confirm_delete.html"
    success_url = reverse_lazy("tracks-web-list")
