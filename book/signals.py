from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from book.models import IssuedBook
from lms.settings import EMAIL_HOST_USER


@receiver(post_save, sender=IssuedBook)
def email_send(sender, instance, created, update_fields, **kwargs):
    if created:
        msg = 'hello ' + str(instance.user.name) + ', You have requested book ' + str(instance.book.name)
        send_mail(
            'Book Issue Request',
            msg,
            EMAIL_HOST_USER,
            [instance.user.email],
            fail_silently=False,
        )
