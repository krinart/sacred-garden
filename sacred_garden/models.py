import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from sacred_garden.managers import CustomUserManager


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


class EmotionalNeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)


class EmotionalNeedValue(models.Model):
    emotional_need = models.ForeignKey(EmotionalNeed, on_delete=models.CASCADE)
    value = models.IntegerField()
    partner_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


def create_emotional_need_value(user, eneed, value):
    EmotionalNeedValue.objects.filter(
        emotional_need=eneed,
        is_current=True,
    ).update(
        is_current=False,
    )

    return EmotionalNeedValue.objects.create(
        emotional_need=eneed,
        value=value,
        partner_user=user.partner_user,
    )


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
    set_current_user_emotional_need_values_to_partner(user1, user2)

    user2.partner_user = user1
    user2.partner_invite_code = None
    user2.save()
    set_current_user_emotional_need_values_to_partner(user2, user1)


def set_current_user_emotional_need_values_to_partner(user, partner_user):
    EmotionalNeedValue.objects.filter(
        emotional_need__user=user,
        is_current=True
    ).update(
        partner_user=partner_user
    )


def disconnect_partner(user):
    partner_user = user.partner_user

    user.partner_user = None
    user.populate_partner_invite_code()
    user.save()

    partner_user.partner_user = None
    partner_user.populate_partner_invite_code()
    partner_user.save()
