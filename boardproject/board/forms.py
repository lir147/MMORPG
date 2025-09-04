from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Announcement, Response

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'category', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),  # Добавьте TinyMCE для rich-editor
        }

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }