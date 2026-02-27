import json
import urllib.request
import urllib.error
# NOTICE: We completely removed the Google imports to bypass the SDK bugs.

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count
from projects.models import Project
from .models import Task, PeerReview
from textblob import TextBlob 

# --- 1. BOARD LOGIC ---
def board_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)
    
    if request.headers.get('HX-Request'):
        pass 
    
    return render(request, 'board.html', {'project': project, 'tasks': tasks})

def add_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.user != project.owner:
        messages.error(request, "Only the Project Admin can create new tasks.")
        return redirect('board_view', project_id=project.id)

    if request.method == "POST":
        title = request.POST.get('title')
        Task.objects.create(
            title=title, 
            project=project, 
            status='TODO',
            assigned_to=None 
        )
    return redirect('board_view', project_id=project_id)

def update_task(request, task_id, new_status):
    task = get_object_or_404(Task, id=task_id)
    task.status = new_status
    
    if new_status == 'DONE':
        task.assigned_to = request.user
    elif new_status == 'TODO':
        task.assigned_to = None
        
    task.save()
    
    response = HttpResponse("")
    response['HX-Trigger'] = 'refreshBoard' 
    return response

# --- 2. ANALYTICS LOGIC ---
def project_analytics(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    status_data = Task.objects.filter(project=project)\
        .values('status')\
        .annotate(total=Count('id'))
        
    contribution_data = Task.objects.filter(project=project, status='DONE')\
        .values('assigned_to__username')\
        .annotate(total=Count('id'))\
        .order_by('-total')

    context = {
        'project': project,
        'status_data': list(status_data),
        'contribution_data': list(contribution_data)
    }
    return render(request, 'analytics.html', context)

# --- 3. PEER REVIEW LOGIC ---
def submit_review(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == "POST":
        reviewee_id = request.POST.get('reviewee_id')
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')
        
        blob = TextBlob(feedback)
        if blob.sentiment.polarity < -0.5:
            print("WARNING: Toxic review detected!") 

        PeerReview.objects.create(
            reviewer=request.user,
            reviewee_id=reviewee_id,
            rating=rating,
            feedback=feedback
        )
        return redirect('board_view', project_id=project_id)

    return render(request, 'collaboration/review_form.html', {'project': project})

# --- 4. AI TASK GENERATION LOGIC (ZERO-DEPENDENCY DIRECT API CALL) ---
def generate_ai_tasks(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if not project.gemini_api_key:
        messages.error(request, "Please add a Gemini API Key to your project settings.")
        return redirect('board_view', project_id=project.id)

    try:
        api_key = project.gemini_api_key.strip()
        
    
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

        prompt = f"""
        Act as a senior software architect. 
        Break down the project into 5-7 actionable student tasks.
        
        For each task, provide:
        1. A 'title' (short, descriptive).
        2. A 'guide' (one paragraph) explaining how to do it and why.

        Project: {project.title} - {project.description}

        Return ONLY a JSON list of objects. Do not use markdown backticks.
        [
            {{"title": "Setup Git", "guide": "Initialize a repository..."}},
            {{"title": "Base Layout", "guide": "Create the base.html template..."}}
        ]
        """

        # Structuring the exact payload Google expects
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        # Making the raw HTTP POST request
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))

        # Digging into the JSON response to grab the text
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        
       # Clean markdown backticks just in case the AI adds them
        clean_text = text_response.strip().replace('```json', '').replace('```', '')
        
        # Parse the AI's JSON string into Python dictionaries
        task_data = json.loads(clean_text)
        for item in task_data:
            Task.objects.create(
                project=project,
                title=item['title'],
                description=item['guide'], 
                status='TODO', 
                assigned_to=None 
            )

        messages.success(request, f"Generated {len(task_data)} tasks with AI guides!")

    except urllib.error.HTTPError as e:
        # If the API rejects it, this prints the EXACT reason from Google
        error_body = e.read().decode('utf-8')
        print(f"GOOGLE API REJECTION: {error_body}")
        messages.error(request, "API Error: Check your terminal for the exact rejection reason.")
        
    except Exception as e:
        print(f"GENERAL ERROR: {e}") 
        messages.error(request, "Task Generation failed. Check terminal for details.")

    return redirect('board_view', project_id=project.id)