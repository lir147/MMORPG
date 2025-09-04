from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Response

@receiver(post_save, sender=Response)
def notify_author_on_response(sender, instance, created, **kwargs):
    if created:
        announcement_author_email = instance.announcement.author.email  # предполагается, что автор объявления в поле author
        send_mail(
            subject='Новый отклик на ваше объявление',
            message=f'Пользователь {instance.user.username} откликнулся: {instance.text}',
            from_email=None,
            recipient_list=[announcement_author_email],
        )

@receiver(post_save, sender=Response)
def notify_user_on_acceptance(sender, instance, **kwargs):
    if instance.status == 'accepted':
        send_mail(
            subject='Ваш отклик принят',
            message=f'Ваш отклик на объявление "{instance.announcement.title}" принят.',
            from_email=None,
            recipient_list=[instance.user.email],
        )