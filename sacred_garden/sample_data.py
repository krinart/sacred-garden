from datetime import datetime, timedelta

from sacred_garden import models


def populate_sample_user_data(user):
    sample_user = models.User.objects.get(is_sample=True)

    eneed_user = models.EmotionalNeed.objects.create(
        name="Physical Touch (Sample)",
        user=user,
        is_sample=True,
        state_value_type=0,
    )

    eneed_sample_user = models.EmotionalNeed.objects.create(
        name="Acts of Service (Sample)",
        user=sample_user,
        is_sample=True,
        sample_user_partner=user,
        state_value_type=0,
    )

    create_self_emotional_need_states(eneed_user, sample_user)
    create_partner_emotional_need_states(eneed_sample_user, user)

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


def _create_eneed_state(eneed, partner, status, trend, text, text_appreciation, day):
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
        partner_user=partner,
    )

    state.created_at = datetime.now() + timedelta(days=day-30)
    state.save()


def create_self_emotional_need_states(eneed_user, sample_user):
    _create_eneed_state(eneed_user, sample_user, -10, 1, "", "", 0)
    _create_eneed_state(
        eneed_user, sample_user, -10, 0,
        "It would be great if you could hug me at least once a day",
        "I love you very much and very glad that I have you in my life", 1)
    _create_eneed_state(
        eneed_user, sample_user, -10, 1,
        "It is important for me to have a connection in a form of physical touch with you becase I love you",
        "Thank you for being a great partner and for listening to my needs", 3)
    _create_eneed_state(
        eneed_user, sample_user, -10, -1,
        "",
        "Thank you for always being there for me.", 4)
    _create_eneed_state(
        eneed_user, sample_user, -10, 1,
        "",
        "I admire your strength and determination in everything you do.", 5)
    _create_eneed_state(
        eneed_user, sample_user, 0, 1,
        "",
        "You make me feel cherished and loved in ways I never thought possible.", 8)
    _create_eneed_state(
        eneed_user, sample_user, 0, 0,
        "",
        "I am constantly amazed by your intelligence and creativity.", 9)
    _create_eneed_state(
        eneed_user, sample_user, 0, -1,
        "",
        "You have a heart of gold and your kindness never ceases to amaze me.", 10)
    _create_eneed_state(
        eneed_user, sample_user, 0, 1,
        "",
        "Thank you for being patient with me and always putting up with my quirks.", 12)
    _create_eneed_state(
        eneed_user, sample_user, 0, 0,
        "",
        "", 13)
    _create_eneed_state(
        eneed_user, sample_user, 0, -1,
        "",
        "Thank you for being my best friend and my soulmate.", 15)
    _create_eneed_state(
        eneed_user, sample_user, -10, -1,
        "",
        "I am so grateful for the depth and beauty of our connection.", 20)
    _create_eneed_state(
        eneed_user, sample_user, -10, -1,
        "",
        "I admire your intelligence and how you approach every challenge with grace and wisdom.", 21)
    _create_eneed_state(
        eneed_user, sample_user, -20, -1,
        "",
        "You have a heart full of compassion and empathy, and it inspires me every day.", 22)
    _create_eneed_state(
        eneed_user, sample_user, -20, 0,
        "",
        "Thank you for the little things you do, like making me coffee in the morning or leaving me sweet notes.", 24)
    _create_eneed_state(
        eneed_user, sample_user, -20, -1,
        "",
        "I appreciate how you always respect my boundaries and support my dreams and goals.", 25)


def create_partner_emotional_need_states(eneed_sample_user, user):
    _create_eneed_state(eneed_sample_user, user, -20, 0, "", "", 0)
    _create_eneed_state(
        eneed_sample_user, user, -20, 0,
        "I would feel much more loved if you could help me with my chores",
        "I love you very much and willing to do everything I can to have you in my life", 1)
    _create_eneed_state(
        eneed_sample_user, user, -20, 1,
        "",
        "You are the most caring and loving person I know.", 2)
    _create_eneed_state(
        eneed_sample_user, user, -20, -1,
        "",
        "I appreciate how you always prioritize our relationship and make time for us.", 4)
    _create_eneed_state(
        eneed_sample_user, user, -20, -1,
        "",
        "Thank you for being my partner in everything and always having my back.", 5)
    _create_eneed_state(
        eneed_sample_user, user, -20, 1,
        "",
        "You bring out the best in me and make me want to be a better person.", 6)
    _create_eneed_state(
        eneed_sample_user, user, -10, 1,
        "",
        "You have a beautiful soul that radiates love and positivity.", 8)
    _create_eneed_state(
        eneed_sample_user, user, -10, 0,
        "",
        "Thank you for making me feel cherished and valued, even on my worst days.", 9)
    _create_eneed_state(
        eneed_sample_user, user, -10, 1,
        "",
        "I am so lucky to have you as my partner, and I appreciate everything you do for me and our relationship.", 11)
    _create_eneed_state(
        eneed_sample_user, user, -10, -1,
        "",
        "You make me feel seen, heard, and understood in ways no one else can.", 12)
    _create_eneed_state(
        eneed_sample_user, user, 0, 1,
        "",
        "I appreciate your honesty and how you always speak from the heart.", 15)
    _create_eneed_state(
        eneed_sample_user, user, 0, 0,
        "",
        "You have a remarkable work ethic and a drive to succeed that I deeply admire.", 16)
    _create_eneed_state(
        eneed_sample_user, user, 0, 1,
        "",
        "Thank you for being my partner in adventure and always being up for trying new things with me.", 18)
    _create_eneed_state(
        eneed_sample_user, user, 0, 0,
        "",
        "You have a unique perspective on life that challenges me and helps me grow.", 20)


def create_self_sample_emotional_letters(user, sample_user):
    pass


def create_partner_sample_emotional_letters(user, sample_user):
    pass

