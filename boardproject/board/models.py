import uuid
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_ckeditor_5.widgets import CKEditor5Widget

class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    token_created_at = models.DateTimeField(auto_now_add=True)

    def generate_confirmation_token(self):
        self.confirmation_token = uuid.uuid4()
        self.token_created_at = timezone.now()
        self.save()

    def is_token_valid(self):
        return self.token_created_at >= timezone.now() - timedelta(days=1)


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('tank', 'Танки'),
        ('healer', 'Хилы'),
        ('dd', 'ДД'),
        ('trader', 'Торговцы'),
        ('guildmaster', 'Гилдмастеры'),
        ('questgiver', 'Квестгиверы'),
        ('blacksmith', 'Кузнецы'),
        ('leatherworker', 'Кожевники'),
        ('alchemist', 'Зельевары'),
        ('spellmaster', 'Мастера заклинаний'),
    ]
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return dict(self.CATEGORY_CHOICES).get(self.name, self.name)


class Announcement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


STATUS_CHOICES = [
    ('pending', 'Ожидает'),
    ('accepted', 'Принят'),
    ('rejected', 'Отклонён'),
]


class Response(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Отклик от {self.user.username} на "{self.announcement.title}"'


class NewsletterSubscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} - {"Активен" if self.active else "Отписан"}'


class Newsletter(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.subject