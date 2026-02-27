from django.contrib import admin
from .models import Task, PeerReview

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'assigned_to')
    list_filter = ('status', 'project')

admin.site.register(PeerReview)