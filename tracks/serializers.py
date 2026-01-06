from rest_framework import serializers
from .models import Track

class TrackSerializer(serializers.ModelSerializer):
    def validate_track_popularity(self, v):
        if not (0 <= v <= 100):
            raise serializers.ValidationError("track_popularity must be 0–100.")
        return v

    def validate_artist_popularity(self, v):
        if not (0 <= v <= 100):
            raise serializers.ValidationError("artist_popularity must be 0–100.")
        return v
    
    class Meta:
        model = Track
        fields = "__all__"


class TopArtistSummarySerializer(serializers.Serializer):
    artist_name = serializers.CharField()
    track_count = serializers.IntegerField()
    avg_track_popularity = serializers.FloatField(allow_null=True)
    max_track_popularity = serializers.IntegerField(allow_null=True)
    followers = serializers.FloatField(allow_null=True)


class ReleasesByYearSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    track_count = serializers.IntegerField()
    avg_track_popularity = serializers.FloatField(allow_null=True)
    explicit_count = serializers.IntegerField()


class GenreCountSerializer(serializers.Serializer):
    genre = serializers.CharField()
    count = serializers.IntegerField()


class CleanHitsSerializer(serializers.Serializer):
    filters = serializers.DictField()
    summary = serializers.DictField()
    top_tracks = TrackSerializer(many=True)


class ArtistAlbumTypeBreakdownSerializer(serializers.Serializer):
    artist_name = serializers.CharField()
    album_type = serializers.CharField()
    track_count = serializers.IntegerField()
    avg_track_popularity = serializers.FloatField(allow_null=True)