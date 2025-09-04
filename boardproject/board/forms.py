from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Announcement
from django_ckeditor_5.widgets import CKEditor5Widget

class AnnouncementForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'category', 'image']

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False  # неактивен до подтверждения через email
        if commit:
            user.save()
        return user

