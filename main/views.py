from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import cloudinary.uploader

from .models import Project, ProjectImage, SiteContent
from .serializers import (
    ProjectSerializer,
    ProjectWriteSerializer,
    SiteContentSerializer,
)
from .spotify import (
    SpotifyAPIError,
    SpotifyConfigurationError,
    empty_spotify_payload,
    get_spotify_payload,
)


def index(request):
    projects = Project.objects.all()
    return render(request, 'index.html', {
        "projects": projects,
    })


class SiteContentView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @swagger_auto_schema(
        operation_summary="Get site content",
        operation_description="Returns complete site content (hero, about, skills, testimonials, experience, contact).",
        responses={200: SiteContentSerializer}
    )
    def get(self, request, *args, **kwargs):
        content = SiteContent.get_solo()
        serializer = SiteContentSerializer(content)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update site content",
        operation_description="Updates site content (admin only).",
        request_body=SiteContentSerializer,
        responses={200: SiteContentSerializer}
    )
    def put(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"error": "Admin privileges required."}, status=status.HTTP_403_FORBIDDEN)
        
        content = SiteContent.get_solo()
        serializer = SiteContentSerializer(content, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Admin login",
        operation_description="Authenticate admin user and return JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username or Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            }
        ),
        responses={200: "JWT tokens and user info", 401: "Invalid credentials"}
    )
    def post(self, request, *args, **kwargs):
        username = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if not (user.is_staff or user.is_superuser):
            return Response({"error": "Access denied. Admin privileges required."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
            }
        })


class AuthMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
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
        responses={200: ProjectSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProjectCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"error": "Admin privileges required."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        gallery_images = data.pop('gallery_images', None) or data.pop('images', None)
        
        if isinstance(data.get('technologies'), list):
            data['technologies'] = ", ".join(data['technologies'])

        serializer = ProjectWriteSerializer(data=data)
        if serializer.is_valid():
            project = serializer.save()

            if gallery_images and isinstance(gallery_images, list):
                img_objs = []
                for item in gallery_images:
                    url = item.get('image') if isinstance(item, dict) else item
                    if url and isinstance(url, str):
                        pi = ProjectImage.objects.create(project=project, image=url)
                        img_objs.append(pi)
                project.images.set(img_objs)

            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Project, pk=pk)

    def put(self, request, pk, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"error": "Admin privileges required."}, status=status.HTTP_403_FORBIDDEN)

        project = self.get_object(pk)
        data = request.data.copy()
        gallery_images = data.pop('gallery_images', None)
        if gallery_images is None:
            gallery_images = data.pop('images', None)

        if isinstance(data.get('technologies'), list):
            data['technologies'] = ", ".join(data['technologies'])

        serializer = ProjectWriteSerializer(project, data=data, partial=True)
        if serializer.is_valid():
            updated_project = serializer.save()

            if gallery_images is not None and isinstance(gallery_images, list):
                # Delete existing gallery images and recreate in the exact user-specified order
                ProjectImage.objects.filter(project=updated_project).delete()
                img_objs = []
                for item in gallery_images:
                    url = item.get('image') if isinstance(item, dict) else item
                    if url and isinstance(url, str):
                        pi = ProjectImage.objects.create(project=updated_project, image=url)
                        img_objs.append(pi)
                updated_project.images.set(img_objs)

            return Response(ProjectSerializer(updated_project).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"error": "Admin privileges required."}, status=status.HTTP_403_FORBIDDEN)

        project = self.get_object(pk)
        project.delete()
        return Response({"message": "Project deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"error": "Admin privileges required."}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get('file') or request.FILES.get('image')
        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if settings.USE_CLOUDINARY:
                res = cloudinary.uploader.upload(file, folder="portfolio")
                url = res.get("secure_url") or res.get("url")
            else:
                saved_path = default_storage.save(f"uploads/{file.name}", file)
                url = default_storage.url(saved_path)
                if not url.startswith('http'):
                    url = request.build_absolute_uri(url)

            return Response({"url": url}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            return Response(payload, status=status.HTTP_200_OK)
        except SpotifyAPIError:
            payload = empty_spotify_payload()
            payload["error"] = "Spotify is unavailable."
            return Response(payload, status=status.HTTP_200_OK)

