from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name="index"),
    path("api/spotify/now-playing/", SpotifyNowPlayingAPIView.as_view(), name="spotify-now-playing"),
    path("projects/", ProjectListAPIView.as_view(), name="project-list"),
    path("projects/<slug:slug>/", ProjectDetailAPIView.as_view(), name="project-detail"),
]
