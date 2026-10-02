from django.urls import path
from .views import (
    index,
    SiteContentView,
    AdminLoginView,
    AuthMeView,
    ProjectListAPIView,
    ProjectDetailAPIView,
    ProjectCreateView,
    ProjectUpdateDeleteView,
    FileUploadView,
    SpotifyNowPlayingAPIView,
)

urlpatterns = [
    path('', index, name="index"),
    # Site Content
    path("api/content/", SiteContentView.as_view(), name="site-content"),
    
    # Auth
    path("api/auth/login/", AdminLoginView.as_view(), name="admin-login"),
    path("api/auth/me/", AuthMeView.as_view(), name="auth-me"),
    
    # Projects
    path("projects/", ProjectListAPIView.as_view(), name="project-list"),
    path("projects/<slug:slug>/", ProjectDetailAPIView.as_view(), name="project-detail"),
    path("api/projects/create/", ProjectCreateView.as_view(), name="project-create"),
    path("api/projects/<int:pk>/", ProjectUpdateDeleteView.as_view(), name="project-update-delete"),
    
    # File upload
    path("api/upload/", FileUploadView.as_view(), name="file-upload"),
    
    # Spotify
    path("api/spotify/now-playing/", SpotifyNowPlayingAPIView.as_view(), name="spotify-now-playing"),
]
