import base64
import json
import os
from typing import Any
from urllib import parse, request
from urllib.error import HTTPError, URLError

from django.core.cache import cache


SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_CURRENTLY_PLAYING_URL = "https://api.spotify.com/v1/me/player/currently-playing"
SPOTIFY_RECENTLY_PLAYED_URL = "https://api.spotify.com/v1/me/player/recently-played?limit=1"
SPOTIFY_CACHE_KEY = "spotify:now-playing"
SPOTIFY_CACHE_SECONDS = int(os.environ.get("SPOTIFY_CACHE_SECONDS", "5"))
SPOTIFY_TIMEOUT_SECONDS = 8


class SpotifyConfigurationError(Exception):
    pass


class SpotifyAPIError(Exception):
    pass


def empty_spotify_payload() -> dict[str, Any]:
    return {
        "isPlaying": False,
        "title": None,
        "artist": None,
        "album": None,
        "albumImageUrl": None,
        "songUrl": None,
        "playedAt": None,
    }


def get_spotify_payload() -> dict[str, Any]:
    cached_payload = cache.get(SPOTIFY_CACHE_KEY)
    if cached_payload is not None:
        return cached_payload

    access_token = _get_access_token()
    payload = _get_currently_playing(access_token)

    if payload is None:
        payload = _get_recently_played(access_token) or empty_spotify_payload()

    cache.set(SPOTIFY_CACHE_KEY, payload, SPOTIFY_CACHE_SECONDS)
    return payload


def _get_spotify_credentials() -> tuple[str, str, str]:
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    refresh_token = os.environ.get("SPOTIFY_REFRESH_TOKEN")

    if not client_id or not client_secret or not refresh_token:
        raise SpotifyConfigurationError("Spotify credentials are not configured.")

    return client_id, client_secret, refresh_token


def _get_access_token() -> str:
    client_id, client_secret, refresh_token = _get_spotify_credentials()
    credentials = f"{client_id}:{client_secret}".encode("utf-8")
    auth_header = base64.b64encode(credentials).decode("utf-8")
    form_data = parse.urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
    ).encode("utf-8")

    response = _request_json(
        SPOTIFY_TOKEN_URL,
        method="POST",
        data=form_data,
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    access_token = response.get("access_token")
    if not access_token:
        raise SpotifyAPIError("Spotify token refresh did not return an access token.")

    return access_token


def _get_currently_playing(access_token: str) -> dict[str, Any] | None:
    response = _request_json(
        SPOTIFY_CURRENTLY_PLAYING_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        allowed_statuses={200, 204},
    )

    if response is None or not response.get("is_playing"):
        return None

    track = response.get("item")
    if not track or track.get("type") != "track":
        return None

    return _format_track(track, is_playing=True)


def _get_recently_played(access_token: str) -> dict[str, Any] | None:
    response = _request_json(
        SPOTIFY_RECENTLY_PLAYED_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    items = response.get("items") or []
    if not items:
        return None

    latest_item = items[0]
    track = latest_item.get("track")
    if not track:
        return None

    payload = _format_track(track, is_playing=False)
    payload["playedAt"] = latest_item.get("played_at")
    return payload


def _format_track(track: dict[str, Any], is_playing: bool) -> dict[str, Any]:
    album = track.get("album") or {}
    images = album.get("images") or []
    external_urls = track.get("external_urls") or {}
    artists = track.get("artists") or []

    return {
        "isPlaying": is_playing,
        "title": track.get("name"),
        "artist": ", ".join(artist.get("name", "") for artist in artists if artist.get("name")),
        "album": album.get("name"),
        "albumImageUrl": images[0].get("url") if images else None,
        "songUrl": external_urls.get("spotify"),
        "playedAt": None,
    }


def _request_json(
    url: str,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    allowed_statuses: set[int] | None = None,
) -> dict[str, Any] | None:
    allowed_statuses = allowed_statuses or {200}
    spotify_request = request.Request(url, data=data, headers=headers or {}, method=method)

    try:
        with request.urlopen(spotify_request, timeout=SPOTIFY_TIMEOUT_SECONDS) as response:
            if response.status not in allowed_statuses:
                raise SpotifyAPIError(f"Spotify returned status {response.status}.")
            if response.status == 204:
                return None
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except HTTPError as exc:
        if exc.code in allowed_statuses and exc.code == 204:
            return None
        raise SpotifyAPIError(f"Spotify returned status {exc.code}.") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise SpotifyAPIError("Spotify request failed.") from exc
