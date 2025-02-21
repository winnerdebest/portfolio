from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from main.sitemaps import StaticViewSitemap, ProjectSitemap  # Import from your main app

def robots_txt(request):
    ROBOTS_TXT = "User-agent: *\nDisallow:"
    return HttpResponse(ROBOTS_TXT, content_type="text/plain")

sitemaps = {
    'static': StaticViewSitemap,
    'projects': ProjectSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),  # Include your app's URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps, 'content_type': 'application/xml'}, name='sitemap'),
    path("robots.txt", robots_txt, name="robots_txt"),
]
