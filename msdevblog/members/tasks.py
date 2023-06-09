from celery import shared_task
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.contrib.auth import get_user_model


@shared_task
def task_send_mail(subject: str, message: str, from_email: str = None, **kwargs) -> int:
    return send_mail(subject, message, from_email, **kwargs)


@shared_task
def task_send_mail_reset_password(subject_template_name, email_template_name, context,
                                  from_email, to_email, html_email_template_name):
    context['user'] = get_user_model().objects.get(pk=context['user'])

    PasswordResetForm.send_mail(
        None,
        subject_template_name=subject_template_name,
        email_template_name=email_template_name,
        context=context,
        from_email=from_email,
        to_email=to_email,
        html_email_template_name=html_email_template_name
    )
