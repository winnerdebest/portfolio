from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from .models import Project

SITE_URL = settings.SITE_URL.rstrip("/")  # Ensure no trailing slash

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ['index', 'projects']

    def location(self, item):
        return reverse(item)  # Return only the relative path

class ProjectSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Project.objects.all()

    def location(self, obj):
        return reverse('project_detail', args=[obj.slug])  # Return relative path
