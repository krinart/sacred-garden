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

    state.created_at = datetime.now() + timedelta(days=day-60)
    state.save()


def create_self_emotional_need_states(eneed_user, sample_user):
    _create_eneed_state(eneed_user, sample_user, -10, 1, "", "", 0)
    _create_eneed_state(
        eneed_user, sample_user, -10, 0,
        "It would be great if you could hug me at least once a day",
        "I love you very much and very glad that I have you in my life", 1)
    _create_eneed_state(
        eneed_user, sample_user, -10, 1,
        "It is important for me to have a connection in a form of physical touch with you because I love you",
        "Thank you for being a great partner and for listening to my needs", 3)
    _create_eneed_state(
        eneed_user, sample_user, -10, -1,
        "In the past several days I wish I could get more physical touch from you",
        "Thank you for surprising me with breakfast in bed this morning. You always know how to make my day.", 8)
    _create_eneed_state(
        eneed_user, sample_user, -10, 1,
        "I felt much better because you gave me more attention. Thank you!",
        "I appreciate how you always take the time to listen to me and understand my feelings, even when I'm being irrational.", 11)
    _create_eneed_state(
        eneed_user, sample_user, 0, 1,
        "Great work! Please keep it up",
        "Your dedication to your career is inspiring, and I am so proud of everything you have accomplished.", 14)
    _create_eneed_state(
        eneed_user, sample_user, 0, 0,
        "Good job. I am proud of you",
        "Thank you for planning such a thoughtful and romantic date for us last night. You always know how to make me feel special.", 18)
    _create_eneed_state(
        eneed_user, sample_user, 0, -1,
        "It would be great if you could give me a hug every morning after we wake up",
        "I am grateful for your unwavering support and encouragement as I pursue my own dreams and goals.", 21)
    _create_eneed_state(
        eneed_user, sample_user, 0, 1,
        "Thank you for listening to my desires!",
        "You have a talent for making me laugh even on my toughest days, and I appreciate your sense of humor so much.", 23)
    _create_eneed_state(
        eneed_user, sample_user, 0, 0,
        "I am again grateful for what you are doing. Good job :)",
        "Thank you for always putting our relationship first and making time for us, even when life gets busy.", 26)
    _create_eneed_state(
        eneed_user, sample_user, 0, -1,
        "I am very grateful for what you already did. Please give me a hug when I am returning from work",
        "Your kindness and generosity towards others is something I admire so much about you.", 29)
    _create_eneed_state(
        eneed_user, sample_user, -10, -1,
        "I know you are busy yourself, but it is very important for me to have a physical touch from you",
        "I appreciate how you always go above and beyond to help me, like picking up groceries when I'm too busy to go myself.", 31)
    _create_eneed_state(
        eneed_user, sample_user, -10, -1,
        "I know it's been hard week. But I am starting to feel unloved without a physical connection",
        "Your creativity and artistic talent never cease to amaze me, and I feel so lucky to witness it every day.", 36)
    _create_eneed_state(
        eneed_user, sample_user, -20, -1,
        "Please pay more attention to this need, it has become a serious problem.",
        "I appreciate how you always show up for me, whether it's to support me through a tough time or to celebrate a happy moment.", 42)
    _create_eneed_state(
        eneed_user, sample_user, -20, 0,
        "I appreciate all you did, but I still don't feel loved enough.",
        "I am grateful for the small acts of kindness you do for me every day, like bringing me a cup of tea when I'm feeling stressed.", 46)
    _create_eneed_state(
        eneed_user, sample_user, -20, -1,
        "I start getting thoughts about physical touch with other people. I don't like those thoughts, so I wish you could help me with this. Thank you!",
        "Your willingness to take responsibility for your mistakes and work to grow from them is something that I respect so much about you.", 50)


def create_partner_emotional_need_states(eneed_sample_user, user):
    _create_eneed_state(eneed_sample_user, user, -20, 0, "", "", 0)
    _create_eneed_state(
        eneed_sample_user, user, -20, 0,
        "I would feel much more loved if you could help me with my chores",
        "I love you very much and willing to do everything I can to have you in my life", 1)
    _create_eneed_state(
        eneed_sample_user, user, -20, 1,
        "",
        "I appreciate how you always make an effort to connect with my family and friends and build relationships with them.", 2)
    _create_eneed_state(
        eneed_sample_user, user, -20, -1,
        "",
        "Your commitment to taking care of your health and well-being inspires me to do the same for myself.", 4)
    _create_eneed_state(
        eneed_sample_user, user, -20, -1,
        "",
        "Your unwavering love and devotion to me make me feel so cherished and valued, and I am so grateful to have you in my life.", 5)
    _create_eneed_state(
        eneed_sample_user, user, -20, 1,
        "",
        "I appreciate how you always show up for me, whether it's to support me through a tough time or to celebrate a happy moment.", 6)
    _create_eneed_state(
        eneed_sample_user, user, -10, 1,
        "",
        "Thank you for being my partner in adventure and always being willing to try new things with me.", 8)
    _create_eneed_state(
        eneed_sample_user, user, -10, 0,
        "",
        "I appreciate how you always go above and beyond to help me, like picking up groceries when I'm too busy to go myself.", 9)
    _create_eneed_state(
        eneed_sample_user, user, -10, 1,
        "",
        "I am so lucky to have you as my partner, and I appreciate everything you do for me and our relationship.", 11)
    _create_eneed_state(
        eneed_sample_user, user, -10, -1,
        "",
        "You have a talent for making me laugh even on my toughest days, and I appreciate your sense of humor so much.", 12)
    _create_eneed_state(
        eneed_sample_user, user, 0, 1,
        "",
        "Thank you for planning such a thoughtful and romantic date for us last night. You always know how to make me feel special.", 15)
    _create_eneed_state(
        eneed_sample_user, user, 0, 0,
        "",
        "Your dedication to your career is inspiring, and I am so proud of everything you have accomplished.", 16)
    _create_eneed_state(
        eneed_sample_user, user, 0, 1,
        "",
        "Thank you for surprising me with breakfast in bed this morning. You always know how to make my day.", 18)
    _create_eneed_state(
        eneed_sample_user, user, 0, 0,
        "",
        "I appreciate how you always take the time to listen to me and understand my feelings, even when I'm being irrational.", 20)


def create_self_sample_emotional_letters(user, sample_user):
    pass


def create_partner_sample_emotional_letters(user, sample_user):
    pass

