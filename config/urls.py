# config/urls.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from projects.views import delete_project_file

# --- Import views neatly grouped by app ---
from projects import views
from users.views import profile_settings, register_view, login_view, logout_view

from projects.views import (
    project_matchmaking, request_join, manage_team, 
    create_project, project_files, project_chat, edit_project, delete_project 
)
from collaboration.views import (
    board_view, add_task, update_task, project_analytics, 
    submit_review, generate_ai_tasks 
)

def home(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),

    # --- AUTHENTICATION URLS ---
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # --- PROJECTS ---
    path('projects/find/', project_matchmaking, name='find_projects'),
    path('projects/create/', create_project, name='create_project'),
    path('project/<int:project_id>/join/', request_join, name='request_join'),
    path('project/<int:project_id>/manage/', manage_team, name='manage_team'),
    path('project/<int:project_id>/files/', project_files, name='project_files'),
    path('project/<int:project_id>/chat/', project_chat, name='project_chat'),

    # --- COLLABORATION ---
    path('project/<int:project_id>/board/', board_view, name='board_view'),
    path('project/<int:project_id>/add/', add_task, name='add_task'),
    path('task/<int:task_id>/update/<str:new_status>/', update_task, name='update_task'),
    path('project/<int:project_id>/analytics/', project_analytics, name='project_analytics'),
    path('project/<int:project_id>/review/', submit_review, name='submit_review'),
    
    # --- NEW AI FEATURE ---
    path('project/<int:project_id>/generate-ai-tasks/', generate_ai_tasks, name='generate_ai_tasks'),
    path('project/<int:project_id>/edit/', edit_project, name='edit_project'),
    path('project/<int:project_id>/delete/', delete_project, name='delete_project'),
    path('file/<int:file_id>/delete/', delete_project_file, name='delete_project_file'),
    path('profile/', profile_settings, name='profile_settings'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)