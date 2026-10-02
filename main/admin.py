from django.contrib import admin
from .models import Project, ProjectImage, SiteContent


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured', 'updated_at')
    list_editable = ('is_featured',)
    prepopulated_fields = {"slug": ("name",)}


class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'contact_email', 'updated_at')


admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectImage)
admin.site.register(SiteContent, SiteContentAdmin)
