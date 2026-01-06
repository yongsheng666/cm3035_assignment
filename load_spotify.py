import os
import csv
import json
from datetime import datetime
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cm3035_assignment.settings")
django.setup()

from tracks.models import Track
from tracks.serializers import TrackSerializer


DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "spotify_data clean.csv")
BATCH_SIZE = 500


def parse_bool(v):
    return str(v).strip().lower() in ("true", "1", "yes", "y")


def parse_int(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default


def parse_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def parse_date(v):
    return datetime.strptime(v.strip(), "%Y-%m-%d").date()


def load_data():
    Track.objects.all().delete()

    batch = []
    total = 0

    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            track = Track(
                track_id=row["track_id"],
                track_name=row["track_name"],
                track_number=parse_int(row["track_number"]),
                track_popularity=parse_int(row["track_popularity"]),
                explicit=parse_bool(row["explicit"]),
                artist_name=row["artist_name"],
                artist_popularity=parse_int(row["artist_popularity"]),
                artist_followers=parse_int(row["artist_followers"]),
                artist_genres=(row.get("artist_genres") or "").strip(),
                album_id=row["album_id"],
                album_name=row["album_name"],
                album_release_date=parse_date(row["album_release_date"]),
                album_total_tracks=parse_int(row["album_total_tracks"]),
                album_type=row["album_type"],
                track_duration_min=parse_float(row["track_duration_min"]),
            )

            batch.append(track)

            if len(batch) >= BATCH_SIZE:
                Track.objects.bulk_create(
                    batch,
                    ignore_conflicts=True,
                )
                total += len(batch)
                batch.clear()

        # final remainder
        if batch:
            Track.objects.bulk_create(
                batch,
                ignore_conflicts=True,
            )
            total += len(batch)

    print(f"Loaded {total} tracks successfully.")


def dump_sample_json():
    qs = Track.objects.all()[:20]
    serializer = TrackSerializer(qs, many=True)
    print(json.dumps(serializer.data, indent=2, default=str))


if __name__ == "__main__":
    load_data()
    dump_sample_json()
