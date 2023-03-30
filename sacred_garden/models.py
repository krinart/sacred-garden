from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .managers import CustomUserManager

import random
import string


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    partner_user = models.OneToOneField('self', models.CASCADE, blank=True, null=True)
    partner_name = models.CharField(max_length=50, blank=True, null=True)
    partner_invite_code = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def populate_partner_invite_code(self):
        self.partner_invite_code = get_new_invite_code()


def get_new_invite_code(n=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, n=n))


@receiver(pre_save, sender=User)
def populate_partner_invite_code_for_new_user(sender, instance, update_fields, **kwargs):

    # When user is created
    if instance.pk is None and instance.partner_invite_code is None:
        instance.populate_partner_invite_code()

    # When partner is disconnected and invite code is empty
    # is_partner_disconnected = 'partner_user' in update_fields and instance.partner_user is None
    # is_invite_code_empty = instance.partner_invite_code is None
    # if is_partner_disconnected and is_invite_code_empty :
    #     instance.populate_partner_invite_code()


def connect_partners(user1, user2):
    user1.partner_user = user2
    user1.partner_invite_code = None
    user1.save()

    user2.partner_user = user1
    user2.partner_invite_code = None
    user2.save()
