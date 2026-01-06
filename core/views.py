import sys
import django
from django.shortcuts import render


def index(request):
    context = {
        "python_version": sys.version.split()[0],
        "django_version": django.get_version(),
        "packages_used": [
            "Django",
            "djangorestframework",
        ],
        # Coursework requirement: show admin credentials on the main page.
        # Use simple demo credentials for marking (do NOT reuse real passwords).
        "admin_username": "admin",
        "admin_password": "Admin123!",
        "endpoints": [
            # Frontend
            ("Tracks Frontend (List/Search)", "/tracks/"),
            ("Create Track (Form)", "/tracks/new/"),

            # Admin
            ("Admin Site", "/admin/"),

            # REST API (Core CRUD)
            ("API: List/Create Tracks (GET/POST)", "/api/tracks/"),
            ("API: Track Detail (GET)", "/api/tracks/1/"),

            # REST API (Summary endpoints)
            ("API: Top Artists", "/api/tracks/summary/top-artists/"),
            ("API: Releases By Year", "/api/tracks/summary/releases-by-year/"),
            ("API: Top Genres (top=20)", "/api/tracks/summary/top-genres/?top=20"),
            ("API: Clean Hits (complex filter)", "/api/tracks/insights/clean-hits/?min_popularity=80&genre=pop&year_from=2019&year_to=2021&album_type=album"),
            ("API: Artist Album Type Breakdown", "/api/tracks/insights/artist-albumtype-breakdown/?artist=drake"),

            # Swagger/OpenAPI (optional; enable only if you install drf-spectacular)
            ("OpenAPI Schema (JSON)", "/api/schema/"),
            ("Swagger UI", "/api/docs/"),

           

        ],
    }
    return render(request, "core/index.html", context)
