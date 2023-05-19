from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.signing import Signer

from msdevblog.settings import ALLOWED_HOSTS, DEFAULT_FROM_EMAIL

signer = Signer()       # Используем для создания цифровой подписи


def send_activation_notification(user):
    """
    Отправляет электронной письмо пользователю, который регистрируется на сайте
    для подтверждения адреса электронной почты.
    """
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'
    # В качестве уникального и стойкого к подделке идентификатора пользователя применяем его имя,
    # защищенное цифровой подписью. Создание цифровой подписи выполняем посредством класса Signer."
    context = {'user': user, 'host': host, 'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.txt', context)
    body_text = render_to_string('email/activation_letter_body.txt', context)
    send_mail(subject,
              body_text,
              from_email=DEFAULT_FROM_EMAIL,
              recipient_list=[user.email],
              fail_silently=True)
