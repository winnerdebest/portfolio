from django.contrib import admin
from .models import *



class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured', 'updated_at')
    list_editable = ('is_featured',)
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectImage)

