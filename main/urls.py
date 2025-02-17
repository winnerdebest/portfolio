from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name="index"),
    path('projects/', projects, name="projects"),
    path("project/<slug:slug>/", projects, name="project_detail"),
]
