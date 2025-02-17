from django.shortcuts import render, get_object_or_404
from .models import *


# Create your views here.
def index(request):
    projects = Project.objects.all()
    return render(request, 'index.html', {
        "projects": projects,
    })

def projects(request, slug):
    project = get_object_or_404(Project, slug=slug)
    images = project.images.all()  # Fetch all images related to the project
    technologies = project.get_technologies_list()  # Get technologies as a list

    context = {
        "project": project,
        "images": images,
        "technologies": technologies
    }
    return render(request, 'projects/projects.html', context)