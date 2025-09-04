from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.views import View
from .models import User, Announcement, Response, Category
from .forms import RegistrationForm, AnnouncementForm, ResponseForm
from django.conf import settings



@login_required
def my_responses(request):
    announcements = Announcement.objects.filter(author=request.user)
    responses = Response.objects.filter(announcement__in=announcements)

    announcement_id = request.GET.get('announcement')
    if announcement_id:
        responses = responses.filter(announcement_id=announcement_id)

    return render(request, 'my_responses.html', {
        'responses': responses,
        'announcements': announcements,
    })

@login_required
def accept_response(request, response_id):
    response = get_object_or_404(Response, pk=response_id, announcement__author=request.user)
    response.status = 'accepted'
    response.save()
    return redirect('my_responses')

@login_required
def delete_response(request, response_id):
    response = get_object_or_404(Response, pk=response_id, announcement__author=request.user)
    response.delete()
    return redirect('my_responses')

def index(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'announcement_list.html', {'announcements': announcements})

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'registration.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.generate_confirmation_code()
            user.save()
            # Исправлено: использование правильного адреса отправителя
            send_mail(
                'Подтверждение регистрации',
                f'Код подтверждения: {user.confirmation_code}',
                settings.DEFAULT_FROM_EMAIL,  # Замена на реальный email из settings
                [user.email],
            )
            messages.success(request, 'Проверьте email, чтобы подтвердить регистрацию.')
            return redirect('confirm_registration')
        return render(request, 'registration.html', {'form': form})

def confirm_registration(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        user = User.objects.filter(confirmation_code=code).first()
        if user:
            user.is_active = True
            user.email_confirmed = True
            user.confirmation_code = ''
            user.save()
            login(request, user)
            messages.success(request, 'Регистрация подтверждена!')
            return redirect('index')
        messages.error(request, 'Неверный код подтверждения')
    return render(request, 'confirm_registration.html')

@login_required
def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.user = request.user
            announcement.save()
            messages.success(request, 'Объявление создано.')
            return redirect('index')
    else:
        form = AnnouncementForm()
    return render(request, 'create_announcement.html', {'form': form})

@login_required
def edit_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление обновлено.')
            return redirect('index')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'edit_announcement.html', {'form': form})

def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    responses = announcement.response_set.all()
    return render(request, 'announcement_detail.html', {
        'announcement': announcement,
        'responses': responses,
    })

@login_required
def submit_response(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.announcement = announcement
            response.user = request.user
            response.save()
            # Исправлено: использование правильного адреса отправителя
            send_mail(
                f'Новый отклик на ваше объявление "{announcement.title}"',
                f'От: {request.user.username}\nТекст: {response.text}',
                settings.DEFAULT_FROM_EMAIL,  # Замена на реальный email из settings
                [announcement.user.email],
            )
            messages.success(request, 'Отклик отправлен владельцу объявления.')
            return redirect('announcement_detail', pk=pk)
    else:
        form = ResponseForm()
    return render(request, 'submit_response.html', {'form': form, 'announcement': announcement})

@login_required
def manage_responses(request):
    categories = Category.objects.all()
    responses = Response.objects.filter(announcement__user=request.user)
    # Фильтрация по категории, если выставлен GET-параметр
    category_filter = request.GET.get('category')
    if category_filter:
        responses = responses.filter(announcement__category__name=category_filter)
    if request.method == 'POST':
        response_id = request.POST.get('response_id')
        action = request.POST.get('action')
        response = get_object_or_404(Response, pk=response_id, announcement__user=request.user)
        if action == 'delete':
            response.delete()
            messages.success(request, 'Отклик удалён.')
        elif action == 'accept':
            response.accepted = True
            response.save()
            # Исправлено: использование правильного адреса отправителя
            send_mail(
                'Ваш отклик принят!',
                f'Объявление: {response.announcement.title}',
                settings.DEFAULT_FROM_EMAIL,  # Замена на реальный email из settings
                [response.user.email],
            )
            messages.success(request, 'Отклик принят, пользователь уведомлен.')
        # После POST - редирект на ту же страницу, чтобы не было повторной отправки формы
        return redirect('manage_responses')
    return render(request, 'manage_responses.html', {
        'responses': responses,
        'categories': categories,
        'category_filter': category_filter,
    })