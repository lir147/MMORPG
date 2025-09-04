from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .forms import RegistrationForm, AnnouncementForm, ResponseForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import User, Announcement, Response, NewsletterSubscriber
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
import logging  # Для логирования ошибок отправки email


logging.basicConfig(level=logging.INFO)

@login_required
def edit_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление обновлено')
            return redirect('index')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'edit_announcement.html', {'form': form})

@login_required
def delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk, user=request.user)  # Только владелец может удалить
    announcement.delete()
    messages.success(request, 'Объявление удалено.')
    return redirect('index')

# Оставлена одна функция submit_response с email-уведомлением
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

            # Отправка уведомления владельцу объявления о новом отклике
            subject = 'Новый отклик на ваше объявление'
            message_text = (
                f'Здравствуйте!\n\nПользователь {response.user.username} ответил на ваше объявление "{announcement.title}".\n\n'
                f'Текст отклика: {response.text}\n\n'
                f'Посмотреть: {request.build_absolute_uri(reverse("announcement_detail", args=[pk]))}'
            )
            try:
                send_mail(
                    subject,
                    message_text,
                    settings.DEFAULT_FROM_EMAIL,
                    [announcement.user.email],
                    fail_silently=False,
                )
                logging.info('Email о новом отклике отправлен на %s', announcement.user.email)
            except Exception as e:
                logging.error('Ошибка при отправке email о новом отклике: %s', str(e))
                messages.warning(request, 'Не удалось отправить уведомление о новом отклике.')

            messages.success(request, 'Отклик отправлен владельцу объявления.')
            return redirect('announcement_detail', pk=pk)
    else:
        form = ResponseForm()
    return render(request, 'submit_response.html', {'form': form, 'announcement': announcement})

@login_required
def reset_response_to_pending(request, response_id):
    response = get_object_or_404(Response, id=response_id, announcement__user=request.user)
    response.status = 'pending'
    response.save()
    messages.success(request, 'Статус отклика сброшен на "ожидает".')

    # НОВОЕ: Отправка уведомления пользователю о сбросе статуса
    subject = 'Статус вашего отклика изменён'
    message_text = (
        f'Здравствуйте, {response.user.username}!\n\n'
        f'Владелец объявления "{response.announcement.title}" изменил статус вашего отклика на "ожидает".\n\n'
        f'Текст отклика: {response.text}\n\n'
        f'Посмотреть: {request.build_absolute_uri(reverse("announcement_detail", args=[response.announcement.pk]))}'
    )
    try:
        send_mail(
            subject,
            message_text,
            settings.DEFAULT_FROM_EMAIL,
            [response.user.email],
            fail_silently=False,
        )
        logging.info('Email о сбросе статуса отклика отправлен на %s', response.user.email)
    except Exception as e:
        logging.error('Ошибка при отправке email о сбросе статуса: %s', str(e))
        messages.warning(request, 'Не удалось отправить уведомление о сбросе статуса.')

    return redirect('manage_responses')

@login_required
def accept_response(request, response_id):
    response = get_object_or_404(Response, id=response_id, announcement__user=request.user)
    response.status = 'accepted'
    response.save()
    messages.success(request, 'Отклик принят.')

    # Отправка уведомления пользователю о принятии отклика
    subject = 'Ваш отклик принят'
    message_text = (
        f'Здравствуйте, {response.user.username}!\n\n'
        f'Владелец объявления "{response.announcement.title}" принял ваш отклик.\n\n'
        f'Текст отклика: {response.text}\n\n'
        f'Посмотреть: {request.build_absolute_uri(reverse("announcement_detail", args=[response.announcement.pk]))}'
    )
    try:
        send_mail(
            subject,
            message_text,
            settings.DEFAULT_FROM_EMAIL,
            [response.user.email],
            fail_silently=False,
        )
        logging.info('Email о принятии отклика отправлен на %s', response.user.email)
    except Exception as e:
        logging.error('Ошибка при отправке email о принятии: %s', str(e))
        messages.warning(request, 'Не удалось отправить уведомление о принятии отклика.')

    return redirect('manage_responses')

@login_required
def reject_response(request, response_id):
    response = get_object_or_404(Response, id=response_id, announcement__user=request.user)
    response.status = 'rejected'
    response.save()
    messages.success(request, 'Отклик отклонён.')

    # Отправка уведомления пользователю об отклонении отклика
    subject = 'Ваш отклик отклонён'
    message_text = (
        f'Здравствуйте, {response.user.username}!\n\n'
        f'Владелец объявления "{response.announcement.title}" отклонил ваш отклик.\n\n'
        f'Текст отклика: {response.text}\n\n'
        f'Посмотреть: {request.build_absolute_uri(reverse("announcement_detail", args=[response.announcement.pk]))}'
    )
    try:
        send_mail(
            subject,
            message_text,
            settings.DEFAULT_FROM_EMAIL,
            [response.user.email],
            fail_silently=False,
        )
        logging.info('Email об отклонении отклика отправлен на %s', response.user.email)
    except Exception as e:
        logging.error('Ошибка при отправке email об отклонении: %s', str(e))
        messages.warning(request, 'Не удалось отправить уведомление об отклонении отклика.')

    return redirect('manage_responses')

@login_required
def delete_response(request, response_id):
    response = get_object_or_404(Response, id=response_id, announcement__user=request.user)

    # Сохраняем данные для email ПЕРЕД удалением объекта
    user_email = response.user.email
    username = response.user.username
    announcement_title = response.announcement.title
    response_text = response.text

    response.delete()
    messages.success(request, 'Отклик удалён.')

    # Отправка уведомления пользователю об удалении отклика
    subject = 'Ваш отклик удалён'
    message_text = (
        f'Здравствуйте, {username}!\n\n'
        f'Владелец объявления "{announcement_title}" удалил ваш отклик.\n\n'
        f'Текст отклика: {response_text}'
    )
    try:
        send_mail(
            subject,
            message_text,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logging.info('Email об удалении отклика отправлен на %s', user_email)
    except Exception as e:
        logging.error('Ошибка при отправке email об удалении: %s', str(e))
        messages.warning(request, 'Не удалось отправить уведомление об удалении отклика.')

    return redirect('manage_responses')

# Классы и остальные функции оставлены без изменений
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
            try:
                send_mail(
                    'Подтвердите регистрацию',
                    f'Чтобы завершить регистрацию, перейдите по ссылке:\n{confirm_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.warning(request, 'Не удалось отправить письмо подтверждения.')
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
        form = AnnouncementForm(request.POST, request.FILES)
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
def manage_responses(request):
    responses = Response.objects.filter(announcement__user=request.user)
    return render(request, 'manage_responses.html', {'responses': responses})

@login_required
def edit_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление обновлено')
            return redirect('index')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'edit_announcement.html', {'form': form})

def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    responses = announcement.response_set.all()
    form = ResponseForm()
    return render(request, 'announcement_detail.html', {
        'announcement': announcement,
        'responses': responses,
        'form': form
    })

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
        try:
            send_mail(
                'Новостная рассылка',
                message,
                settings.DEFAULT_FROM_EMAIL,
                emails,
                fail_silently=False,
            )
        except Exception as e:
            messages.warning(request, 'Не удалось отправить рассылку.')
        messages.success(request, 'Новостная рассылка отправлена.')
        return redirect('index')
    return render(request, 'send_newsletter.html')

@csrf_exempt
def ckeditor_5_upload_file(request):
    if request.method == 'POST' and request.FILES:
        upload = next(iter(request.FILES.values()))
        saved_path = default_storage.save(upload.name, upload)
        url = default_storage.url(saved_path)
        return JsonResponse({'url': url})
    return JsonResponse({'error': 'Invalid request'}, status=400)