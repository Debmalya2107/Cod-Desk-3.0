from django import forms
from django.core.validators import FileExtensionValidator
from taggit.forms import TagWidget
from .models import Project, ProjectFile, ProjectMessage

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'thumbnail', 'required_skills', 'gemini_api_key']
        widgets = {
            'required_skills': TagWidget(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g. python, django, css'
            }),
        }

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        # Add 'custom_name' to the fields list
        fields = ['file', 'name'] 
        widgets = {
            'file': forms.FileInput(attrs={'accept': '.enc', 'class': 'hidden'}),
            'name': forms.HiddenInput(), # Keep it hidden, we will fill it via JS
        }
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['enc'])])
class MessageForm(forms.ModelForm):
    class Meta:
        model = ProjectMessage
        fields = ['content']