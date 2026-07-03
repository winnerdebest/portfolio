import os
from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from .spotify import SpotifyAPIError, get_spotify_payload
from .views import SpotifyNowPlayingAPIView


SPOTIFY_ENV = {
    "SPOTIFY_CLIENT_ID": "client-id",
    "SPOTIFY_CLIENT_SECRET": "client-secret",
    "SPOTIFY_REFRESH_TOKEN": "refresh-token",
}


class SpotifyNowPlayingTests(SimpleTestCase):
    def setUp(self):
        cache.delete("spotify:now-playing")

    @patch.dict(os.environ, SPOTIFY_ENV)
    @patch("main.spotify._request_json")
    def test_returns_currently_playing_track(self, mock_request_json):
        mock_request_json.side_effect = [
            {"access_token": "access-token"},
            {
                "is_playing": True,
                "item": {
                    "type": "track",
                    "name": "Song title",
                    "artists": [{"name": "Artist name"}],
                    "album": {
                        "name": "Album name",
                        "images": [{"url": "https://image.example/cover.jpg"}],
                    },
                    "external_urls": {"spotify": "https://open.spotify.com/track/1"},
                },
            },
        ]

        payload = get_spotify_payload()

        self.assertTrue(payload["isPlaying"])
        self.assertEqual(payload["title"], "Song title")
        self.assertEqual(payload["artist"], "Artist name")
        self.assertEqual(payload["album"], "Album name")
        self.assertEqual(payload["albumImageUrl"], "https://image.example/cover.jpg")
        self.assertEqual(payload["songUrl"], "https://open.spotify.com/track/1")
        self.assertIsNone(payload["playedAt"])

    @patch.dict(os.environ, SPOTIFY_ENV)
    @patch("main.spotify._request_json")
    def test_falls_back_to_recently_played_when_nothing_is_playing(self, mock_request_json):
        mock_request_json.side_effect = [
            {"access_token": "access-token"},
            {"is_playing": False, "item": None},
            {
                "items": [
                    {
                        "played_at": "2026-07-03T10:15:00Z",
                        "track": {
                            "name": "Last song",
                            "artists": [{"name": "Recent artist"}],
                            "album": {"name": "Recent album", "images": []},
                            "external_urls": {"spotify": "https://open.spotify.com/track/2"},
                        },
                    }
                ]
            },
        ]

        payload = get_spotify_payload()

        self.assertFalse(payload["isPlaying"])
        self.assertEqual(payload["title"], "Last song")
        self.assertEqual(payload["artist"], "Recent artist")
        self.assertEqual(payload["album"], "Recent album")
        self.assertIsNone(payload["albumImageUrl"])
        self.assertEqual(payload["songUrl"], "https://open.spotify.com/track/2")
        self.assertEqual(payload["playedAt"], "2026-07-03T10:15:00Z")

    @patch.dict(os.environ, SPOTIFY_ENV)
    @patch("main.spotify._request_json")
    def test_raises_when_token_refresh_fails(self, mock_request_json):
        mock_request_json.return_value = {}

        with self.assertRaises(SpotifyAPIError):
            get_spotify_payload()

    @patch("main.views.get_spotify_payload")
    def test_view_returns_safe_error_payload_when_spotify_fails(self, mock_get_spotify_payload):
        mock_get_spotify_payload.side_effect = SpotifyAPIError("token refresh failed")
        request = APIRequestFactory().get("/api/spotify/now-playing/")

        response = SpotifyNowPlayingAPIView.as_view()(request)

        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.data["isPlaying"])
        self.assertEqual(response.data["error"], "Spotify is unavailable.")
