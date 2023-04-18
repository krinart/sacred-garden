from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase
from django.urls import reverse
from rest_framework import exceptions
from rest_framework.test import APIClient
from rest_framework_jwt.serializers import jwt_decode_handler

from collections import OrderedDict

from sacred_garden import models

from unittest import mock

from sacred_garden.test_views import ApiTestCase


class TestSampleData(ApiTestCase):

    def setUp(self):
        self.sample_user = models.User.objects.create(
            email='sample@example.com',
            is_active=False,
            is_sample=True,
        )

        self.user = models.User.objects.create(
            email='user@example.com',
            partner_user=self.sample_user,
            has_sample_data=True)
        self.other_user = models.User.objects.create(email='other_user@example.com', partner_user=self.sample_user)

        letter_user_to_sample = models.EmotionalLetter.objects.create(sender=self.user, recipient=self.sample_user)
        letter_sample_to_user = models.EmotionalLetter.objects.create(sender=self.sample_user, recipient=self.user)

        letter_other_to_sample = models.EmotionalLetter.objects.create(sender=self.other_user,
                                                                       recipient=self.sample_user)
        letter_sample_to_other = models.EmotionalLetter.objects.create(sender=self.sample_user,
                                                                       recipient=self.other_user)

        self.eneed_user = models.EmotionalNeed.objects.create(user=self.user, name='hugs', state_value_type=0)
        self.eneed_other_user = models.EmotionalNeed.objects.create(user=self.other_user, name='hugs', state_value_type=0)
        self.eneed_sample_user_user = models.EmotionalNeed.objects.create(
            user=self.sample_user, name='hugs_user', state_value_type=0,
            is_sample=True, sample_user_partner=self.user)
        self.eneed_sample_user_other_user = models.EmotionalNeed.objects.create(
            user=self.sample_user, name='hugs_other_user', state_value_type=0,
            is_sample=True, sample_user_partner=self.other_user)

        models.create_emotional_need_state(self.user, self.eneed_user, 0, 0, 0, "", "")
        self.eneed_state_user = models.create_emotional_need_state(self.user, self.eneed_user, -10, -1, 0, "", "")

        models.create_emotional_need_state(self.other_user, self.eneed_other_user, 0, 0, 0, "", "")
        models.create_emotional_need_state(self.other_user, self.eneed_other_user, -20, -2, 0, "", "")

        models.create_emotional_need_state(self.sample_user, self.eneed_sample_user_user, 0, 0, 0, "", "")
        self.eneed_state_sample_user = models.create_emotional_need_state(self.sample_user, self.eneed_sample_user_user, 0, 0, 0, "", "")

        models.create_emotional_need_state(self.sample_user, self.eneed_sample_user_other_user, 0, 0, 0, "", "")
        models.create_emotional_need_state(self.sample_user, self.eneed_sample_user_other_user, 0, 0, 0, "", "")

    def test_counts(self):
        self.assertEqual(models.User.objects.filter(partner_user=self.sample_user).count(), 2)

        self.assertEqual(models.EmotionalLetter.objects.count(), 4)
        self.assertEqual(models.EmotionalNeed.objects.count(), 4)
        self.assertEqual(models.EmotionalNeedState.objects.count(), 8)

    def test_user_api(self):
        response = self.request_get('user-me', auth_user=self.user)
        self.assertSuccess(response)

        del response.data['emotional_needs'][0]['current_state']['created_at']
        del response.data['partner_user']['emotional_needs'][0]['current_state']['created_at']
        del response.data['partner_invite_code']

        self.assertEqual(
            response.data,
            {
                'id': self.user.id,
                'has_sample_data': True,
                'first_name': '',
                'email': 'user@example.com',
                'partner_user': OrderedDict([
                    ('id', self.sample_user.id),
                    ('first_name', ''),
                    ('emotional_needs', [
                        OrderedDict([
                            ('id', self.eneed_sample_user_user.id),
                            ('name', 'hugs_user'),
                            ('current_state', OrderedDict([
                                ('emotional_need_id', self.eneed_sample_user_user.id),
                                ('status', 0),
                                ('value_abs', 0),
                                ('value_rel', 0),
                                ('id', self.eneed_state_sample_user.id),
                                ('text', ''),
                                ('appreciation_text', ''),
                                # ('created_at', '2023-04-18T05:00:55.147223Z'),
                                ('is_initial_state', False)])),
                            ('state_value_type', 0),
                            ('user', self.sample_user.id)])])]),
                'partner_name': None,
                # 'partner_invite_code': 'JT5XKV',
                'unread_letters_count': 1,
                'emotional_needs': [
                    OrderedDict([
                        ('id', self.eneed_user.id),
                        ('name', 'hugs'),
                        ('current_state', OrderedDict([
                            ('emotional_need_id', self.eneed_user.id),
                            ('status', -10),
                            ('value_abs', -1),
                            ('value_rel', 0),
                            ('id', self.eneed_state_user.id),
                            ('text', ''),
                            ('appreciation_text', ''),
                            # ('created_at', '2023-04-18T05:00:55.135904Z'),
                            ('is_initial_state', False)])),
                        ('state_value_type', 0),
                        ('user', self.user.id)]),
                ]
            }
        )
