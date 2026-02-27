from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your custom User model so you can edit skills
admin.site.register(User, UserAdmin)