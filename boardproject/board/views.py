from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .forms import RegistrationForm, AnnouncementForm
from .models import User, Announcement, NewsletterSubscriber, Category
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class CustomRegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'registration.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.generate_confirmation_token()
            confirm_url = request.build_absolute_uri(
                reverse('confirm_registration') + f'?token={user.confirmation_token}'
            )
            send_mail(
                'Подтвердите регистрацию',
                f'Чтобы завершить регистрацию, перейдите по ссылке:\n{confirm_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            messages.success(request, 'Регистрация успешна! Проверьте email для подтверждения.')
            return redirect('login')
        return render(request, 'registration.html', {'form': form})

class ConfirmRegistrationView(View):
    def get(self, request):
        token = request.GET.get('token')
        user = User.objects.filter(confirmation_token=token).first()
        if not user:
            messages.error(request, 'Неверный токен подтверждения')
            return redirect('register')
        if not user.is_token_valid():
            messages.error(request, 'Срок действия токена истёк')
            return redirect('register')
        user.email_confirmed = True
        user.is_active = True
        user.confirmation_token = None
        user.save()
        messages.success(request, 'Email подтверждён. Теперь вы можете войти.')
        return redirect('login')

@method_decorator(login_required, name='dispatch')
class CreateAnnouncementView(View):
    def get(self, request):
        form = AnnouncementForm()
        return render(request, 'create_announcement.html', {'form': form})

    def post(self, request):
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.user = request.user
            announcement.save()
            messages.success(request, 'Объявление создано')
            return redirect('index')
        return render(request, 'create_announcement.html', {'form': form})

def index(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'announcement_list.html', {'announcements': announcements})

@login_required
def subscribe_newsletter(request):
    sub, _ = NewsletterSubscriber.objects.get_or_create(user=request.user)
    sub.active = True
    sub.save()
    messages.success(request, 'Вы подписаны на новости.')
    return redirect('index')

@login_required
def unsubscribe_newsletter(request):
    sub = NewsletterSubscriber.objects.filter(user=request.user).first()
    if sub:
        sub.active = False
        sub.save()
    messages.success(request, 'Вы отписаны от новостей.')
    return redirect('index')

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods

@staff_member_required
@require_http_methods(["GET", "POST"])
def send_newsletter(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if not message:
            messages.error(request, 'Текст сообщения не может быть пустым.')
            return redirect('send_newsletter')
        subscribers = NewsletterSubscriber.objects.filter(active=True).select_related('user')
        emails = [s.user.email for s in subscribers if s.user.email]
        send_mail(
            'Новостная рассылка',
            message,
            settings.DEFAULT_FROM_EMAIL,
            emails,
        )
        messages.success(request, 'Новостная рассылка отправлена.')
        return redirect('index')
    return render(request, 'send_newsletter.html')