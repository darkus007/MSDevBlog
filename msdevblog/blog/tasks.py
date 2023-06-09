from django.core.mail import send_mail

from celery import shared_task


@shared_task
def send_feedback_mail(subject: str, message: str, from_email: str, recipient_list: list | tuple):
    """ Отправляет сообщение, обертка над 'send_mail' с целью использования в Celery """
    return send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
