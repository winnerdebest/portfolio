from rest_framework import serializers
from .models import Project, ProjectImage


class ProjectImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ['id', 'image']

    def get_image(self, obj):
        if hasattr(obj.image, 'url'):
            return obj.image.url
        return None


class ProjectSerializer(serializers.ModelSerializer):
    preview_image = serializers.SerializerMethodField()
    technologies = serializers.SerializerMethodField()
    images = ProjectImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'slug',
            'short_description',
            'description',
            'preview_image',
            'technologies',
            'images',
            'project_link',
            'is_featured',
            'updated_at',
        ]

    def get_preview_image(self, obj):
        if hasattr(obj.preview_image, 'url'):
            return obj.preview_image.url
        return None

    def get_technologies(self, obj):
        return obj.get_technologies_list()
