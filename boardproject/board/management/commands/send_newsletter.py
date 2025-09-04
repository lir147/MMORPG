from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from django.utils import timezone
from board.models import Newsletter, User

class Command(BaseCommand):
    help = 'Отправляет новостную рассылку'

    def handle(self, *args, **options):
        newsletter = Newsletter.objects.filter(sent_at__isnull=True).first()
        if newsletter:
            recipients = [user.email for user in User.objects.filter(email_confirmed=True)]
            messages = [(newsletter.subject, newsletter.content, 'from@example.com', [email]) for email in recipients]
            send_mass_mail(messages, fail_silently=False)
            newsletter.sent_at = timezone.now()
            newsletter.save()
            self.stdout.write('Рассылка отправлена!')
        else:
            self.stdout.write('Нет новых рассылок.')