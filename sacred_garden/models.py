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

    partner_user = models.ForeignKey('self', models.CASCADE, blank=True, null=True)
    partner_name = models.CharField(max_length=50, blank=True, null=True)
    partner_invite_code = models.CharField(max_length=50, blank=True, null=True, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def populate_partner_invite_code(self):
        self.partner_invite_code = get_new_invite_code()


def get_new_invite_code(k=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))


@receiver(pre_save, sender=User)
def populate_partner_invite_code_for_new_user(instance, **kwargs):

    # When user is being created (before saving)
    if instance.pk is None:
        initialize_user(instance)


def initialize_user(user):
    if user.partner_invite_code is None:
        user.populate_partner_invite_code()


def get_user_by_partner_invite_code(partner_invite_code):
    return User.objects.get(partner_invite_code=partner_invite_code)


def connect_partners(user1, user2):
    user1.partner_user = user2
    user1.partner_invite_code = None
    user1.save()

    user2.partner_user = user1
    user2.partner_invite_code = None
    user2.save()


def disconnect_partners(user1, user2):
    user1.partner_user = None
    user1.populate_partner_invite_code()
    user1.save()

    user2.partner_user = None
    user2.populate_partner_invite_code()
    user2.save()
