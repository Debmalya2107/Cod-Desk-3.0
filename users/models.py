from django.contrib.auth.models import AbstractUser
from django.db import models
from taggit.managers import TaggableManager

class User(AbstractUser):
    is_student = models.BooleanField(default=True)
    skills = TaggableManager(help_text="e.g., Python, React, Data Analysis", blank=True) 
    portfolio_link = models.URLField(blank=True)
    
    # --- NEW PROFILE FIELDS ---
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True,
        help_text="Upload a professional photo or avatar."
    )
    
    bio = models.TextField(
        blank=True, 
        help_text="Tell us about yourself, your background, and the projects you want to build!"
    )

    def __str__(self):
        return self.username