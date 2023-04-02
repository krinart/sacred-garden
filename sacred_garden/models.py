import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from sacred_garden import managers


PREFETCHED_CURRENT_VALUES_ATTR_NAME = "current_emotionalneedstatus_set"


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    partner_user = models.ForeignKey('self', models.CASCADE, blank=True, null=True)
    partner_name = models.CharField(max_length=50, blank=True, null=True)
    partner_invite_code = models.CharField(max_length=50, blank=True, null=True, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = managers.UserManager()

    def __str__(self):
        return self.email

    def populate_partner_invite_code(self):
        self.partner_invite_code = get_new_invite_code()


class EmotionalNeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.name} ({self.user})'

    @property
    def current_status(self):
        if not hasattr(self, PREFETCHED_CURRENT_VALUES_ATTR_NAME):
            return self.emotionalneedstatus_set.get(is_current=True)

        if self.current_emotionalneedstatus_set:
            return self.current_emotionalneedstatus_set[0]

        raise EmotionalNeedStatus.DoesNotExist


class EmotionalNeedStatus(models.Model):
    class StatusChoices(models.IntegerChoices):
        GOOD = 0
        BAD = -10
        PROBLEM = -20

    class TrendChoices(models.IntegerChoices):
        NEGATIVE = -1
        NEUTRAL = 0
        POSITIVE = 1

    emotional_need = models.ForeignKey(EmotionalNeed, on_delete=models.CASCADE)
    status = models.IntegerField(choices=StatusChoices.choices)
    trend = models.IntegerField(choices=TrendChoices.choices)
    partner_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                     related_name='partner_emotional_need_values_set')
    is_current = models.BooleanField(default=True)
    appreciation_text = models.TextField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.status}: {self.emotional_need.name} ({self.emotional_need.user})'


def create_emotional_need_value(user, eneed, status, trend, text, appreciation_text):
    EmotionalNeedStatus.objects.filter(
        emotional_need=eneed,
        is_current=True,
    ).update(
        is_current=False,
    )

    return EmotionalNeedStatus.objects.create(
        emotional_need=eneed,
        status=status,
        trend=trend,
        partner_user=user.partner_user,
        text=text,
        appreciation_text=appreciation_text,
    )


def get_new_invite_code(k=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))


# @receiver(post_save, sender=EmotionalNeed)
# def post_save_emotional_need(instance, created, **kwargs):
#     if created:
#         create_emotional_need_value(instance.user, instance, 0)

@receiver(pre_save, sender=User)
def pre_save_user(instance, **kwargs):

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
    EmotionalNeedStatus.objects.filter(
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



def get_emotional_needs_with_prefetched_current_values(user=None):
    qs = EmotionalNeed.objects.prefetch_related(
        models.Prefetch(
            'emotionalneedstatus_set',
            queryset=EmotionalNeedStatus.objects.filter(is_current=True),
            to_attr=PREFETCHED_CURRENT_VALUES_ATTR_NAME,
        )
    )

    if user:
        qs = qs.filter(user=user)

    return qs
