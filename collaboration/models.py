from django.db import models
from django.conf import settings

class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
    ]
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    
    # assigned_to is used for the "Pull System" leaderboard logic
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    
    # NEW: Stores the AI-generated mentor guide/purpose for the task
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class PeerReview(models.Model):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='reviews_given', 
        on_delete=models.CASCADE
    )
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='reviews_received', 
        on_delete=models.CASCADE
    )
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) # 1-5 Scale
    feedback = models.TextField()

    def __str__(self):
        return f"Review for {self.reviewee.username} by {self.reviewer.username}"