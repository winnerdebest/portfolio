from django.db import models
from django.utils.text import slugify
from django.conf import settings
from cloudinary.models import CloudinaryField

class Project(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=155, blank=True)
    description = models.TextField()
    if settings.USE_CLOUDINARY:
        preview_image = CloudinaryField('projects/previews/', transformation=[
                {'width': 800, 'height': 800, 'crop': 'limit', 'quality': 'auto', 'fetch_format': 'webp'}
            ], default='static/images/Screenshot_21.png')
    else:
        preview_image = models.ImageField(upload_to='projects/previews/', blank=True, null=True)
    technologies = models.TextField(help_text="Enter technologies separated by commas")
    images = models.ManyToManyField('ProjectImage', related_name='project_images', blank=True,)
    project_link = models.URLField()

    def __str__(self):
        return self.name
    
    def get_technologies_list(self):
        return [tech.strip() for tech in self.technologies.split(",") if tech.strip()]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Auto-generate slug from name
        super().save(*args, **kwargs)


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    if settings.USE_CLOUDINARY:
        image = CloudinaryField('projects/images/', transformation=[
                {'width': 800, 'height': 800, 'crop': 'limit', 'quality': 'auto', 'fetch_format': 'webp'}
            ], default='static/images/Screenshot_21.png')
    else:
        image = models.ImageField(upload_to='projects/images/', blank=True, null=True)

    def __str__(self):
        return f"Image for {self.project.name}"
