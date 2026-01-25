from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from main.sitemaps import StaticViewSitemap, ProjectSitemap  # Import from your main app



from rest_framework import permissions
from django.conf.urls.static import static
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="My Portfolio API",
      default_version='v1',
      description="API documentation for My Portfolio",
      contact=openapi.Contact(email="support@myportfolio.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


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
    
    
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
