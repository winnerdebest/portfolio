from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name="index"),
    path("projects/", ProjectListAPIView.as_view(), name="project-list"),
    path("projects/<slug:slug>/", ProjectDetailAPIView.as_view(), name="project-detail"),
]
