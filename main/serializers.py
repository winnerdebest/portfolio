from rest_framework import serializers
from .models import Project, ProjectImage, SiteContent


class ProjectImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ['id', 'image']

    def get_image(self, obj):
        if hasattr(obj.image, 'url'):
            return obj.image.url
        return str(obj.image) if obj.image else None


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
        return str(obj.preview_image) if obj.preview_image else None

    def get_technologies(self, obj):
        return obj.get_technologies_list()


class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'slug',
            'short_description',
            'description',
            'technologies',
            'project_link',
            'is_featured',
            'preview_image',
        ]
        extra_kwargs = {
            'slug': {'required': False},
            'preview_image': {'required': False, 'allow_null': True},
        }


class SiteContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteContent
        fields = [
            'id',
            'hero_title',
            'hero_tagline',
            'typewriter_texts',
            'avatar_url',
            'resume_url',
            'status_badge',
            'about_quote',
            'about_paragraphs',
            'about_tags',
            'skill_categories',
            'testimonials',
            'experiences',
            'contact_email',
            'contact_phone',
            'contact_location',
            'whatsapp_number',
            'github_url',
            'linkedin_url',
            'x_url',
            'updated_at',
        ]

