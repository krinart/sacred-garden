from unittest import mock

from django.test import TestCase

from sacred_garden import models


class TestUserCreate(TestCase):

    @mock.patch('sacred_garden.models.get_new_invite_code')
    def test_invite_code_is_populated(self, mocked_get_new_invite_code):
        mocked_get_new_invite_code.return_value = 'QWE123'

        user = models.User.objects.create()

        user = models.User.objects.get(pk=user.pk)
        self.assertEqual(user.partner_invite_code, 'QWE123')


class TestUserUpdate(TestCase):
    @mock.patch('sacred_garden.models.get_new_invite_code')
    def test_invite_code_is_not_updated(self, mocked_get_new_invite_code):
        mocked_get_new_invite_code.return_value = 'QWE123'

        user = models.User.objects.create(first_name='Jon', partner_invite_code='ALPHA5')

        user.first_name = 'John'
        user.save()

        user = models.User.objects.get(pk=user.pk)
        self.assertEqual(user.partner_invite_code, 'ALPHA5')


class TestConnectPartners(TestCase):

    def test_connect_partners(self):
        user1 = models.User.objects.create(email='user1@example.com', partner_invite_code='CODE_1')
        user2 = models.User.objects.create(email='user2@example.com', partner_invite_code='CODE_2')

        models.connect_partners(user1, user2)

        user1 = models.User.objects.get(pk=user1.pk)
        user2 = models.User.objects.get(pk=user2.pk)

        self.assertEqual(user1.partner_user, user2)
        self.assertEqual(user2.partner_user, user1)

        self.assertIsNone(user1.partner_invite_code)
        self.assertIsNone(user2.partner_invite_code)


class TestDisconnectPartner(TestCase):

    def test_disconnect_partner(self):
        user1 = models.User.objects.create(email='user1@example.com', partner_invite_code='CODE_1')
        user2 = models.User.objects.create(email='user2@example.com', partner_invite_code='CODE_2')

        models.connect_partners(user1, user2)
        models.disconnect_partner(user1)

        user1 = models.User.objects.get(pk=user1.pk)
        user2 = models.User.objects.get(pk=user2.pk)

        self.assertIsNone(user1.partner_user)
        self.assertIsNone(user2.partner_user)

        self.assertIsNotNone(user1.partner_invite_code)
        self.assertIsNotNone(user2.partner_invite_code)


class TestCreateEmotionalNeedValue(TestCase):

    def setUp(self):
        self.user = models.User.objects.create(email='user@example.com')
        self.partner = models.User.objects.create(email='partner@example.com')
        self.user_eneed = models.EmotionalNeed.objects.create(user=self.user, name='Hugs')
        self.partner_eneed = models.EmotionalNeed.objects.create(user=self.partner, name='Lies')

    def assertEmotionalNeedValues(self, eneed, expected_values):
        actual_values = models.EmotionalNeedValue.objects.filter(
            emotional_need=eneed
        ).order_by('created_at')

        n = actual_values.count()
        self.assertEqual(n, len(expected_values))

        values_list = actual_values.values_list('partner_user', 'value', 'is_current')

        for i, ((apartner, avalue, is_current), (epartner, evalue)) in enumerate(zip(values_list, expected_values)):
            self.assertEqual(epartner, apartner)
            self.assertEqual(evalue, avalue)

            if i == n-1:
                self.assertTrue(is_current)
            else:
                self.assertFalse(is_current)

    def test_simple(self):
        self.assertEmotionalNeedValues(self.user_eneed, [(None, 0)])
        self.assertEmotionalNeedValues(self.partner_eneed, [(None, 0)])

        models.create_emotional_need_value(self.user, self.user_eneed, -2)
        self.assertEmotionalNeedValues(self.user_eneed, [(None, 0), (None, -2)])
        self.assertEmotionalNeedValues(self.partner_eneed, [(None, 0)])

        models.create_emotional_need_value(self.user, self.user_eneed, -1)
        self.assertEmotionalNeedValues(self.user_eneed, [(None, 0), (None, -2), (None, -1)])
        self.assertEmotionalNeedValues(self.partner_eneed, [(None, 0)])

        models.connect_partners(self.user, self.partner)
        self.assertEmotionalNeedValues(self.user_eneed, [(None, 0), (None, -2), (self.partner.id, -1)])
        self.assertEmotionalNeedValues(self.partner_eneed, [(self.user.id, 0)])

        models.create_emotional_need_value(self.user, self.user_eneed, 0)
        self.assertEmotionalNeedValues(self.user_eneed, [(None, 0), (None, -2), (self.partner.id, -1), (self.partner.id, 0)])
        self.assertEmotionalNeedValues(self.partner_eneed, [(self.user.id, 0)])
