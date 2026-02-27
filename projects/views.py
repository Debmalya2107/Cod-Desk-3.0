from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Cleaned up and consolidated imports
from .models import Project, ProjectFile, ProjectMessage
from .forms import ProjectForm, FileUploadForm, MessageForm

# --- 1. MATCHMAKING LOGIC ---
def project_matchmaking(request):
    if request.user.is_authenticated:
        user_skills = request.user.skills.all()
        
        if not user_skills:
            matches = Project.objects.all()
        else:
            matches = Project.objects.annotate(
                match_count=Count('required_skills', filter=Q(required_skills__in=user_skills))
            ).order_by('-match_count', '-created_at')
    else:
        matches = Project.objects.all()

    return render(request, 'projects/matchmaking.html', {'projects': matches})

# --- 2. JOIN REQUEST LOGIC ---
@login_required
def request_join(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user not in project.members.all() and request.user != project.owner:
        project.join_requests.add(request.user)
    return redirect('find_projects')

# --- 3. MANAGE TEAM LOGIC ---
@login_required
def manage_team(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.user != project.owner:
        return redirect('find_projects')

    if request.method == "POST":
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        try:
            target_user = project.join_requests.get(id=user_id)
            
            if action == "accept":
                project.members.add(target_user) 
                project.join_requests.remove(target_user) 
            elif action == "reject":
                project.join_requests.remove(target_user)
        except:
            pass 
            
    return render(request, 'projects/manage_team.html', {'project': project})

# --- 4. CREATE PROJECT ---
@login_required
def create_project(request):
    if request.method == 'POST':
        # NEW: Added request.FILES to handle the thumbnail upload
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user  
            project.save()
            form.save_m2m() 
            return redirect('find_projects') 
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create_project.html', {'form': form})

# --- 5. EDIT PROJECT ---
@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.owner:
        messages.error(request, "Only the project owner can edit the settings.")
        return redirect('board_view', project_id=project.id)

    if request.method == 'POST':
        # NEW: Added request.FILES to handle thumbnail updates
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project settings updated successfully!")
            return redirect('board_view', project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/edit_project.html', {'form': form, 'project': project})

# --- 6. PROJECT FILES ---
@login_required
def project_files(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # 🔒 THE BOUNCER: Security Check
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, "Access Denied: You are not a member of this project.")
        return redirect('find_projects')

    files = project.files.all().order_by('-uploaded_at')
    
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES) 
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.project = project
            new_file.uploaded_by = request.user
            new_file.save()
            return redirect('project_files', project_id=project_id)
    else:
        form = FileUploadForm()

    return render(request, 'projects/files.html', {'project': project, 'files': files, 'form': form})

# --- 7. PROJECT CHAT ---
@login_required
def project_chat(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # 🔒 THE BOUNCER: Security Check
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, "Access Denied: You are not a member of this project.")
        return redirect('find_projects')

    # Changed variable name to messages_list so it doesn't conflict with Django messages
    messages_list = project.messages.all().order_by('created_at')
    
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.project = project
            msg.sender = request.user
            msg.save()
            return redirect('project_chat', project_id=project_id)
    else:
        form = MessageForm()

    if request.headers.get('HX-Request'):
        return render(request, 'projects/chat_partial.html', {'messages': messages_list, 'user': request.user})

    return render(request, 'projects/chat.html', {
        'project': project, 
        'messages': messages_list, 
        'form': form
    })

# --- 8. DELETE PROJECT ---
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Security: Only the owner can delete the project
    if request.user == project.owner:
        project.delete()
        messages.success(request, "Project deleted successfully.")
    else:
        messages.error(request, "Access Denied: Only the project admin can delete this project.")
        
    # Send them back to the matchmaking page after deletion
    return redirect('find_projects')

def delete_project_file(request, file_id):
    # Fetch the file object
    file_obj = get_object_or_404(ProjectFile, id=file_id)
    project = file_obj.project

    # SECURITY CHECK: Only allow the project owner to delete
    if request.user == project.owner:
        # 1. Physically delete the .enc file from the server's media folder
        if file_obj.file:
            file_obj.file.delete(save=False)
            
        # 2. Delete the record from the database
        file_obj.delete()
        messages.success(request, f"File deleted successfully.")
    else:
        messages.error(request, "Permission denied. Only the project admin can delete files.")

    # Redirect back to the files page
    return redirect('project_files', project_id=project.id)