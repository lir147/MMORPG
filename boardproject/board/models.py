from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string


class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    confirmation_code = models.CharField(max_length=32, blank=True)

    def generate_confirmation_code(self):
        self.confirmation_code = get_random_string(length=32)
        self.save()

# Категории объявлений
class Category(models.Model):
    name = models.CharField(max_length=50, choices=[
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
    ])

    def __str__(self):
        return self.name

# Объявления
class Announcement(models.Model):
    user = models.ForeignKey('board.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()  # Для HTML-контента
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='announcements/', blank=True)  # Для картинок

    def __str__(self):
        return self.title

# Отклики

STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    ]

class Response(models.Model):
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    user = models.ForeignKey('board.User', on_delete=models.CASCADE)
    text = models.TextField()
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f'Отклик от {self.user} на {self.announcement}'

# Новостные рассылки (через админку)
class Newsletter(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_at = models.DateTimeField(null=True, blank=True)