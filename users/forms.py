# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from taggit.forms import TagWidget # <--- IMPORT ADDED HERE

# Get the custom User model dynamically
User = get_user_model()

class StudentSignUpForm(UserCreationForm):
    # Add an extra field for skills during sign up
    skills = forms.CharField(
        help_text="Separate skills with commas (e.g. Python, Design, Marketing)",
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'skills')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True  # Force them to be a student
        if commit:
            user.save()
            # Save the tags (skills) safely
            if self.cleaned_data.get('skills'):
                user.skills.add(*[s.strip() for s in self.cleaned_data['skills'].split(',') if s.strip()])
        return user

# --- Form for the Profile Settings Page ---
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'portfolio_link', 'skills', 'bio', 'profile_picture']
        
        # Adding Tailwind CSS classes directly to the form inputs for a beautiful UI
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-indigo-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-indigo-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-indigo-500'}),
            'portfolio_link': forms.URLInput(attrs={'class': 'w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-indigo-500', 'placeholder': 'https://...'}),
            
            # --- FIX: Using TagWidget instead of normal TextInput ---
            'skills': TagWidget(attrs={'class': 'w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-indigo-500', 'placeholder': 'e.g. Python, Bootstrap, Android Studio'}),
            
            'bio': forms.Textarea(attrs={'class': 'w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-indigo-500', 'rows': 4, 'placeholder': 'Passionate about building AI models, Java applications...'}),
            'profile_picture': forms.FileInput(attrs={'class': 'w-full border border-gray-300 p-2 rounded bg-gray-50'}),
        }