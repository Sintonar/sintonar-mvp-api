import os
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from sintonar.apps.authentication.models import UserConfirm, UserPhoto
from sintonar.apps.authentication.tasks import task_send_email


@receiver(pre_delete, sender=UserPhoto)
def delete_user_photo_file(sender, instance, **kwargs):
    instance.photos.delete(False)


@receiver(post_save, sender=UserConfirm)
def send_email_confirmation(sender, instance, created, **kwargs):
    if created:
        data = {
            "name": instance.user.first_name,
            "link": os.environ.get("CONFIRM_EMAIL_URL")
            + f"?identification_code={instance.identification_code}",
        }

        task_send_email.delay(
            subject="Confirmação de email",
            to=instance.user.email,
            template="authentication/email_confirmation.html",
            data=data,
        )


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    data = {
        "name": reset_password_token.user.first_name,
        "link": os.environ.get("RESET_PASSWORD_URL")
        + f"?token={reset_password_token.key}",
    }

    task_send_email.delay(
        subject="Recuperação de senha",
        to=reset_password_token.user.email,
        template="authentication/reset_password.html",
        data=data,
    )
