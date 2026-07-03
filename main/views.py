from django.shortcuts import render, get_object_or_404
from .models import *
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Project
from .serializers import ProjectSerializer
from .spotify import (
    SpotifyAPIError,
    SpotifyConfigurationError,
    empty_spotify_payload,
    get_spotify_payload,
)




# Create your views here.
def index(request):
    projects = Project.objects.all()
    return render(request, 'index.html', {
        "projects": projects,
    })


class ProjectListAPIView(ListAPIView):
    queryset = Project.objects.all().order_by("-updated_at")
    serializer_class = ProjectSerializer

    @swagger_auto_schema(
        operation_summary="List all projects",
        operation_description="Returns all portfolio projects",
        responses={200: ProjectSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    

 
    
class ProjectDetailAPIView(RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = "slug"

    @swagger_auto_schema(
        operation_summary="Get a single project",
        operation_description="Retrieve a project using its slug",
        manual_parameters=[
            openapi.Parameter(
                "slug",
                openapi.IN_PATH,
                description="Project slug",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={200: ProjectSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SpotifyNowPlayingAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="Get Spotify now playing",
        operation_description="Returns the current Spotify track, or the most recently played track when nothing is playing.",
        responses={200: openapi.Response("Spotify now-playing payload")},
    )
    def get(self, request, *args, **kwargs):
        try:
            return Response(get_spotify_payload())
        except SpotifyConfigurationError:
            payload = empty_spotify_payload()
            payload["error"] = "Spotify is not configured."
            return Response(payload, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except SpotifyAPIError:
            payload = empty_spotify_payload()
            payload["error"] = "Spotify is unavailable."
            return Response(payload, status=status.HTTP_502_BAD_GATEWAY)
