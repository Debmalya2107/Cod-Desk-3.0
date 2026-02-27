from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager

class Project(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = TaggableManager() 
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='project_thumbnails/', blank=True, null=True)
    
    # Members (Active Team) and Requests (Waiting List)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_projects', blank=True)
    join_requests = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='pending_requests', blank=True)

    # Optional Gemini API Key for AI task generation
    gemini_api_key = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Optional: Enter your Gemini API Key to enable AI task generation."
    )

    def __str__(self):
        return self.title

class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='project_files/')
    
    # This field stores the custom "Display Name" the user enters during upload
    name = models.CharField(max_length=255) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.project.title})"
    
class ProjectMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"