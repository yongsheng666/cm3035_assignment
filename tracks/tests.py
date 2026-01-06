from datetime import date
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import Track


class TrackAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.t1 = Track.objects.create(
            track_id="T001",
            track_name="Song A",
            track_number=1,
            track_popularity=80,
            explicit=False,
            artist_name="Artist 1",
            artist_popularity=70,
            artist_followers=1000000,
            artist_genres="pop, dance pop",
            album_id="ALB1",
            album_name="Album 1",
            album_release_date=date(2020, 1, 1),
            album_total_tracks=10,
            album_type="album",
            track_duration_min=3.5,
        )

    def test_api_list(self):
        r = self.client.get("/api/tracks/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(r.data), 1)

    def test_api_post_create(self):
        payload = {
            "track_id": "T002",
            "track_name": "Song B",
            "track_number": 2,
            "track_popularity": 50,
            "explicit": True,
            "artist_name": "Artist 2",
            "artist_popularity": 60,
            "artist_followers": 500000,
            "artist_genres": "hip hop",
            "album_id": "ALB2",
            "album_name": "Album 2",
            "album_release_date": "2019-05-20",
            "album_total_tracks": 8,
            "album_type": "single",
            "track_duration_min": 4.0,
        }
        r = self.client.post("/api/tracks/", payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)


    def test_clean_hits_endpoint(self):
        r = self.client.get("/api/tracks/insights/clean-hits/?min_popularity=70")
        self.assertEqual(r.status_code, 200)
        self.assertIn("summary", r.data)
        self.assertIn("top_tracks", r.data)

    def test_artist_albumtype_breakdown_requires_artist(self):
        r = self.client.get("/api/tracks/insights/artist-albumtype-breakdown/")
        self.assertEqual(r.status_code, 400)

    def test_post_rejects_invalid_popularity(self):
        payload = {
            "track_id": "bad1",
            "track_name": "Bad Song",
            "track_number": 1,
            "track_popularity": 101,   # invalid
            "explicit": False,
            "artist_name": "Bad Artist",
            "artist_popularity": 50,
            "artist_followers": 10,
            "artist_genres": "pop",
            "album_id": "alb1",
            "album_name": "Bad Album",
            "album_release_date": "2020-01-01",
            "album_total_tracks": 10,
            "album_type": "album",
            "track_duration_min": 3.5,
        }
        r = self.client.post("/api/tracks/", payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("track_popularity", r.data)







class TrackFrontendTests(TestCase):
    def setUp(self):
        self.t1 = Track.objects.create(
            track_id="T100",
            track_name="UI Song",
            track_number=1,
            track_popularity=90,
            explicit=False,
            artist_name="UI Artist",
            artist_popularity=80,
            artist_followers=12345,
            artist_genres="indie",
            album_id="UIALB",
            album_name="UI Album",
            album_release_date=date(2021, 2, 1),
            album_total_tracks=10,
            album_type="album",
            track_duration_min=3.2,
        )

    def test_frontend_list_page(self):
        r = self.client.get("/tracks/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "UI Song")

    def test_frontend_detail_page(self):
        r = self.client.get(f"/tracks/{self.t1.pk}/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "UI Artist")

    def test_frontend_create(self):
        r = self.client.post("/tracks/new/", data={
            "track_id": "T101",
            "track_name": "New UI Song",
            "track_number": 2,
            "track_popularity": 40,
            "explicit": "on",
            "artist_name": "New UI Artist",
            "artist_popularity": 10,
            "artist_followers": 10,
            "artist_genres": "test",
            "album_id": "A101",
            "album_name": "Album 101",
            "album_release_date": "2022-01-01",
            "album_total_tracks": 1,
            "album_type": "single",
            "track_duration_min": 2.5,
        })
        # CreateView redirects on success
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Track.objects.filter(track_id="T101").exists())

    def test_frontend_edit(self):
        r = self.client.post(f"/tracks/{self.t1.pk}/edit/", data={
            "track_id": "T100",
            "track_name": "UI Song Edited",
            "track_number": 1,
            "track_popularity": 90,
            "explicit": "",
            "artist_name": "UI Artist",
            "artist_popularity": 80,
            "artist_followers": 12345,
            "artist_genres": "indie",
            "album_id": "UIALB",
            "album_name": "UI Album",
            "album_release_date": "2021-02-01",
            "album_total_tracks": 10,
            "album_type": "album",
            "track_duration_min": 3.2,
        })
        self.assertEqual(r.status_code, 302)
        self.t1.refresh_from_db()
        self.assertEqual(self.t1.track_name, "UI Song Edited")

    def test_frontend_delete(self):
        r = self.client.post(f"/tracks/{self.t1.pk}/delete/")
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Track.objects.filter(pk=self.t1.pk).exists())


    
