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

    models.EmotionalLetter.objects.filter(
        sender__is_sample=True,
        recipient=user,
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
    l = models.EmotionalLetter.objects.create(
        sender=user,
        recipient=sample_user,
        appreciation_text="Hey love, I just wanted to take a moment to express my deep gratitude for everything you do for me and for us. You are an incredible partner, and I feel so lucky to have you in my life. From the way you support me through the ups and downs, to the way you always make me laugh, and the unwavering love you show me, I truly don't know where I would be without you. Your presence in my life has made everything so much better, and I just wanted to let you know how much I appreciate you. Thank you for being you, and for being such an amazing partner.",
        text="I have something to share with you that happened a few days ago. While I understand that you may not have intended to, your words caused me to feel hurt. I want to clarify that I am not placing blame or accusing you of any wrongdoing. However, I am struggling to process my emotions and would appreciate your support. During our encounter with the sweet couple in the park, I brought up the topic of religion, and you responded with something along the lines of \"please, not this topic again.\" It is important for you to know that discussing this topic is important to me, and despite your initial response, we ended up having a great conversation which they seemed to enjoy. I cannot fully explain why your words impacted me, but it felt as if you were tired of me and did not accept a significant part of who I am.",
        advice_text="I would greatly appreciate it if you could be more accepting of me and refrain from making comments that could be hurtful. While I understand that not everyone is comfortable discussing religion, I would appreciate it if you could trust my judgement when it comes to the topics that I choose to discuss with others. Although I know that you did not mean to upset me, I struggled to process my emotions on my own and now need your help to move past this. Thank you for being understanding, and please know that I love you.",
        is_read=True,
        is_acknowledged=False,
    )

    l.created_at = datetime.now() - timedelta(days=10)
    l.save()



def create_partner_sample_emotional_letters(user, sample_user):
    l = models.EmotionalLetter.objects.create(
        sender=sample_user,
        recipient=user,
        appreciation_text="Hey, I just wanted to take a moment to tell you how much I appreciate you. You are such an amazing partner and I feel so lucky to have you in my life. You always know how to make me laugh and feel better when I'm down, and your unwavering support and encouragement means everything to me. You make me feel loved and appreciated every day, and I am so grateful for your presence in my life. Thank you for being such an incredible partner and for all that you do. I love you.",
        text="There is something important that I want to share with you. Yesterday, we celebrated our anniversary, and I hope you understand just how meaningful this day is to me. As someone who is quite sentimental, I care deeply about commemorating special occasions like this, particularly because our relationship is such an important part of my life and I love you so much. I think you noticed that I had prepared a gift for you that I had made myself, and I hope that you enjoyed it. Unfortunately, what I need to express now is something that has caused me some hurt. It's not about the gift itself, but rather that you didn't give me a gift. I understand that this feeling of hurt stems from my own expectations, but it is still difficult for me to reconcile emotionally. I recognize that our differing attitudes towards gift-giving is a logical explanation, but on an emotional level, I still feel hurt.",
        advice_text="It would mean a lot to me if you could acknowledge that you understand how I feel. This would help me process my emotions and reassure me that our connection is as strong as it usually is. After that, I would love to discuss how we can avoid similar situations in the future and find a compromise that works for both of us. I am willing to adjust my expectations because our relationship is so important to me and I love you deeply. Sending my love to you :)",
        is_read=True,
        is_acknowledged=False,
    )

    l.created_at = datetime.now() - timedelta(days=20)
    l.save()

