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
    is_featured = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


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


class SiteContent(models.Model):
    hero_title = models.CharField(max_length=255, default="I'm Winner.")
    hero_tagline = models.CharField(max_length=255, default="Software Engineer building and deploying SaaS products.")
    typewriter_texts = models.JSONField(default=list, blank=True)
    avatar_url = models.CharField(max_length=500, default="/winners image.jpeg", blank=True)
    resume_url = models.CharField(max_length=500, default="/WinnerOrluVictor_CV.pdf", blank=True)
    status_badge = models.CharField(max_length=100, default="Available for hire", blank=True)

    about_quote = models.TextField(default="If it's complex, tedious, or critical, that's my lane.")
    about_paragraphs = models.JSONField(default=list, blank=True)
    about_tags = models.JSONField(default=list, blank=True)

    skill_categories = models.JSONField(default=list, blank=True)
    testimonials = models.JSONField(default=list, blank=True)
    experiences = models.JSONField(default=list, blank=True)

    contact_email = models.CharField(max_length=150, default="winnerbrown9@gmail.com")
    contact_phone = models.CharField(max_length=50, default="+234 814 231 0497")
    contact_location = models.CharField(max_length=150, default="Rivers State, Nigeria")
    whatsapp_number = models.CharField(max_length=50, default="+2348142310497")
    github_url = models.URLField(default="https://github.com/winnerdebest", blank=True)
    linkedin_url = models.URLField(default="https://linkedin.com/in/winner-orluvictor-944175333", blank=True)
    x_url = models.URLField(default="https://x.com/buildwithwinner", blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Site Content (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        if created or not obj.about_paragraphs:
            obj.populate_defaults()
            obj.save()
        return obj

    def populate_defaults(self):
        if not self.typewriter_texts:
            self.typewriter_texts = ['Full-Stack Engineer', 'SaaS Builder', 'Problem Solver']
        if not self.about_paragraphs:
            self.about_paragraphs = [
                "I'm a Software Engineer with 5+ years of experience building production systems. Not side projects, real products with real users. I've shipped a multi-tenant SaaS platform (QuickCarts) handling escrow payments via Flutterwave, and Paystack. I've built and maintained school management systems, CRMs, and inventory platforms at companies in Nigeria.",
                "I work across the full stack: Python and Django on the backend, React and Next.js on the frontend, PostgreSQL and Supabase for data, and AWS EC2 for deployment. I also run BuildWithWinner, a coding school where I mentor developers from zero to their first deployed application.",
                "If it involves building something complex, maintaining it under pressure, or shipping it fast, that's exactly what I do."
            ]
        if not self.about_tags:
            self.about_tags = ['#Backend', '#Python', '#React', '#DevOps']
        if not self.skill_categories:
            self.skill_categories = [
                {
                    'title': 'Backend',
                    'skills': [
                        { 'name': 'Python', 'iconClass': 'devicon-python-plain colored' },
                        { 'name': 'Django', 'iconClass': 'devicon-django-plain' },
                        { 'name': 'FastAPI', 'iconClass': 'devicon-fastapi-plain colored' },
                    ],
                },
                {
                    'title': 'Frontend',
                    'skills': [
                        { 'name': 'JavaScript', 'iconClass': 'devicon-javascript-plain colored' },
                        { 'name': 'TypeScript', 'iconClass': 'devicon-typescript-plain colored' },
                        { 'name': 'React', 'iconClass': 'devicon-react-original colored' },
                        { 'name': 'Next.js', 'iconClass': 'devicon-nextjs-plain' },
                    ],
                },
                {
                    'title': 'Databases',
                    'skills': [
                        { 'name': 'PostgreSQL', 'iconClass': 'devicon-postgresql-plain colored' },
                        { 'name': 'MongoDB', 'iconClass': 'devicon-mongodb-plain colored' },
                        { 'name': 'Supabase', 'iconClass': 'devicon-supabase-plain colored' },
                    ],
                },
                {
                    'title': 'DevOps & Tools',
                    'skills': [
                        { 'name': 'Docker', 'iconClass': 'devicon-docker-plain colored' },
                        { 'name': 'Git', 'iconClass': 'devicon-git-plain colored' },
                        { 'name': 'AWS', 'iconClass': 'devicon-amazonwebservices-plain-wordmark colored' },
                        { 'name': 'Linux', 'iconClass': 'devicon-linux-plain' },
                    ],
                },
                {
                    'title': 'Design & Product',
                    'skills': [
                        { 'name': 'Figma', 'iconClass': 'devicon-figma-plain colored' },
                    ],
                },
            ]
        if not self.testimonials:
            self.testimonials = [
                {
                    'quote': "Winner has a rare ability to move fast without breaking things. He built and maintained critical features on our platform while keeping the codebase clean and the CI/CD pipeline airtight. Exactly the kind of engineer you want on a production system.",
                    'name': "Team lead",
                    'role': "Career On Track",
                },
                {
                    'quote': "I went from zero to building and deploying my own full-stack app in three months under Winner's mentorship. He doesn't just teach syntax, he teaches how to think like an engineer. Best investment I've made in my career.",
                    'name': "Private student",
                    'role': "BuildWithWinner",
                },
                {
                    'quote': "Winner delivered a complete school management system on time and on budget. He handled everything: backend, frontend, server setup, and was communicative throughout. We still use it daily with zero issues.",
                    'name': "Client",
                    'role': "Serverlink",
                },
            ]
        if not self.experiences:
            self.experiences = [
                {
                    'company': 'Quickcarts',
                    'role': 'Founder & Lead Developer',
                    'duration': 'Present',
                    'current': True,
                    'impact': 'Founder & Lead Developer at Quickcarts.'
                },
                {
                    'company': 'Rivers State ICT Department',
                    'role': 'IT Support Specialist',
                    'duration': '1 year',
                    'current': False,
                    'impact': 'IT Support Specialist at Rivers State ICT Department.'
                },
                {
                    'company': 'Serverlink',
                    'role': 'Web Developer & IT Support',
                    'duration': '6 months',
                    'current': False,
                    'impact': 'Web Developer & IT Support at Serverlink.'
                },
                {
                    'company': 'Career On Track',
                    'role': 'Full Stack Developer',
                    'duration': 'Current',
                    'current': True,
                    'impact': 'Full Stack Developer at Career On Track.'
                },
            ]

