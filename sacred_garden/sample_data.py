from datetime import datetime, timedelta

from sacred_garden import models


def populate_sample_user_data(user):
    sample_user = models.User.objects.get(is_sample=True)

    eneed_user = models.EmotionalNeed.objects.create(
        name="Gifts",
        user=user,
        is_sample=True,
        state_value_type=0,
    )

    eneed_sample_user = models.EmotionalNeed.objects.create(
        name="Gifts",
        user=sample_user,
        is_sample=True,
        sample_user_partner=user,
        state_value_type=0,
    )

    create_self_emotional_need_states(eneed_user)
    create_partner_emotional_need_states(eneed_sample_user)

    create_self_sample_emotional_letters(user, sample_user)
    create_partner_sample_emotional_letters(user, sample_user)

    user.has_sample_data = True
    user.partner_user = sample_user
    user.save()


def clean_sample_user_data(user):
    sample_user = models.User.objects.get(is_sample=True)

    if user.partner_user and user.partner_user.is_sample:
        user.partner_user = None
        user.save()

    models.EmotionalNeed.objects.filter(
        user=user,
        is_sample=True,
    ).delete()

    models.EmotionalNeed.objects.filter(
        user=sample_user,
        sample_user_partner=user,
    ).delete()

    models.EmotionalLetter.objects.filter(
        sender=user,
        recipient__is_sample=True,
    ).delete()

    user.has_sample_data = False
    user.save()


def _create_eneed_state(eneed, status, trend, text, text_appreciation, day):
    models.EmotionalNeedState.objects.filter(
        emotional_need=eneed,
        is_current=True,
    ).update(
        is_current=False,
    )

    state = models.EmotionalNeedState.objects.create(
        emotional_need=eneed,
        status=status,
        value_type=eneed.state_value_type,
        value_abs=None,
        value_rel=trend,
        text=text,
        appreciation_text=text_appreciation,
    )

    state.created_at = datetime.now() + timedelta(days=day-30)
    state.save()


def create_self_emotional_need_states(eneed_user):
    _create_eneed_state(eneed_user, -10, 1, "", "", 0)
    _create_eneed_state(eneed_user, -10, 0, "", "", 1)
    _create_eneed_state(eneed_user, -10, 1, "", "", 3)
    _create_eneed_state(eneed_user, -10, -1, "", "", 4)
    _create_eneed_state(eneed_user, -10, 1, "", "", 5)
    _create_eneed_state(eneed_user, 0, 1, "", "", 8)
    _create_eneed_state(eneed_user, 0, 0, "", "", 9)
    _create_eneed_state(eneed_user, 0, -1, "", "", 10)
    _create_eneed_state(eneed_user, 0, 1, "", "", 12)
    _create_eneed_state(eneed_user, 0, 0, "", "", 13)
    _create_eneed_state(eneed_user, 0, -1, "", "", 15)
    _create_eneed_state(eneed_user, -10, -1, "", "", 20)
    _create_eneed_state(eneed_user, -10, -1, "", "", 21)
    _create_eneed_state(eneed_user, -20, -1, "", "", 22)
    _create_eneed_state(eneed_user, -20, 0, "", "", 24)
    _create_eneed_state(eneed_user, -20, -1, "", "", 25)


def create_partner_emotional_need_states(eneed_sample_user):
    _create_eneed_state(eneed_sample_user, -20, 0, "", "", 0)
    _create_eneed_state(eneed_sample_user, -20, 1, "", "", 1)
    _create_eneed_state(eneed_sample_user, -20, 0, "", "", 2)
    _create_eneed_state(eneed_sample_user, -20, -1, "", "", 4)
    _create_eneed_state(eneed_sample_user, -20, -1, "", "", 5)
    _create_eneed_state(eneed_sample_user, -20, 1, "", "", 6)
    _create_eneed_state(eneed_sample_user, -10, 1, "", "", 8)
    _create_eneed_state(eneed_sample_user, -10, 0, "", "", 9)
    _create_eneed_state(eneed_sample_user, -10, 1, "", "", 11)
    _create_eneed_state(eneed_sample_user, -10, -1, "", "", 12)
    _create_eneed_state(eneed_sample_user, 0, 1, "", "", 15)
    _create_eneed_state(eneed_sample_user, 0, 0, "", "", 16)
    _create_eneed_state(eneed_sample_user, 0, 1, "", "", 18)
    _create_eneed_state(eneed_sample_user, 0, 0, "", "", 20)




def create_self_sample_emotional_letters(user, sample_user):
    pass


def create_partner_sample_emotional_letters(user, sample_user):
    pass

