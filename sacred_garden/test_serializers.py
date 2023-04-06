from django.test import TestCase
from rest_framework import exceptions as drf_exceptions

from sacred_garden import models
from sacred_garden import serializers


RELATIVE = models.EmotionalNeed.StateValueType.RELATIVE
ABSOLUTE = models.EmotionalNeed.StateValueType.ABSOLUTE


class TestEmotionalNeedSerializer(TestCase):

    def test_test(self):
        user = models.User.objects.create()
        eneed1 = models.EmotionalNeed.objects.create(user=user, name='Hug', state_value_type=1)
        models.create_emotional_need_state(user, eneed1, 1, 10, None, "", "")
        ens1 = models.create_emotional_need_state(user, eneed1, 2, 20, None, "", "")

        eneed2 = models.EmotionalNeed.objects.create(user=user, name='Kiss', state_value_type=0)
        models.create_emotional_need_state(user, eneed2, 3, None, 1, "", "")
        ens2 = models.create_emotional_need_state(user, eneed2, 4, None, 1, "", "")

        with self.assertNumQueries(2) as c:
            emotional_needs = models.get_emotional_needs_with_prefetched_current_values(user=user)

            serializer = serializers.EmotionalNeedSerializer(instance=emotional_needs, many=True)
            data = serializer.data

            self.assertEqual(len(data), 2)

            del data[0]['current_state']['created_at']
            del data[1]['current_state']['created_at']

            eneed1_data = {
                'id': eneed1.id,
                'name': 'Hug',
                'state_value_type': 1,
                'current_state': {
                    'id': ens1.id,
                    'emotional_need_id': eneed1.id,
                    'status': 2,
                    'value_abs': 20,
                    'value_rel': None,
                    'text': '',
                    'appreciation_text': '',

                }
            }
            self.assertDictEqual(data[0], eneed1_data)

            eneed2_data = {
                'id': eneed2.id,
                'name': 'Kiss',
                'state_value_type': 0,
                'current_state': {
                    'id': ens2.id,
                    'emotional_need_id': eneed2.id,
                    'status': 4,
                    'value_abs': None,
                    'value_rel': 1,
                    'text': '',
                    'appreciation_text': '',
                }
            }
            # import ipdb; ipdb.set_trace()
            self.assertDictEqual(data[1], eneed2_data)


class MockContext(object):
    def __init__(self, user):
        self.user = user


class TestEmotionalNeedStateSerializer(TestCase):

    def setUp(self):
        self.user = models.User.objects.create()
        self.eneed_relative = models.EmotionalNeed.objects.create(
            user=self.user, name='Hug', state_value_type=RELATIVE)

        self.ens1_relative = models.create_emotional_need_state(self.user, self.eneed_relative, -1, None, 1, "", "")
        self.ens2_relative = models.create_emotional_need_state(self.user, self.eneed_relative, -1, None, -1, "", "")

        self.eneed_absolute = models.EmotionalNeed.objects.create(
            user=self.user, name='Hug', state_value_type=ABSOLUTE)

        self.ens1_absolute = models.create_emotional_need_state(self.user, self.eneed_absolute, -1, 10, None, "", "")
        self.ens2_absolute = models.create_emotional_need_state(self.user, self.eneed_absolute, -1, 20, None, "", "")

    def test_read_relative(self):
        serializer = serializers.EmotionalNeedStateSerializer(
            instance=[self.ens1_relative, self.ens2_relative],
            many=True)
        data = serializer.data
        self.assertEqual(len(data), 2)

        del data[0]['created_at']
        del data[1]['created_at']

        self.assertEqual(
            data[0],
            {
                'id': self.ens1_relative.id,
                'emotional_need_id': self.eneed_relative.id,
                'status': -1,
                'value_abs': 1,
                'value_rel': 1,
                'text': '',
                'appreciation_text': '',
            }
        )

        self.assertEqual(
            data[1],
            {
                'id': self.ens2_relative.id,
                'emotional_need_id': self.eneed_relative.id,
                'status': -1,
                'value_abs': 0,
                'value_rel': -1,
                'text': '',
                'appreciation_text': '',
            }
        )

    def test_read_absolute(self):
        serializer = serializers.EmotionalNeedStateSerializer(
            instance=[self.ens1_absolute, self.ens2_absolute],
            many=True)
        data = serializer.data
        self.assertEqual(len(data), 2)

        del data[0]['created_at']
        del data[1]['created_at']

        self.assertEqual(
            data[0],
            {
                'id': self.ens1_absolute.id,
                'emotional_need_id': self.eneed_absolute.id,
                'status': -1,
                'value_abs': 10,
                'value_rel': None,
                'text': '',
                'appreciation_text': '',
            }
        )

        self.assertEqual(
            data[1],
            {
                'id': self.ens2_absolute.id,
                'emotional_need_id': self.eneed_absolute.id,
                'status': -1,
                'value_abs': 20,
                'value_rel': None,
                'text': '',
                'appreciation_text': '',
            }
        )

    def test_write_relative_requires_value_rel(self):
        data = {
            'emotional_need_id': self.eneed_relative.id,
            'status': -20,
            'text': 'Please help',
            'appreciation_text': 'I love you',
        }
        serializer = serializers.EmotionalNeedStateSerializer(
            data=data,
            context={'request': MockContext(self.user)})

        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertEqual(
            serializer.errors,
            {'value_rel': [drf_exceptions.ErrorDetail(string='This field is required.', code='required')]}
        )

    def test_write_absolute_requires_value_abs(self):
        data = {
            'emotional_need_id': self.eneed_absolute.id,
            'status': -20,
            'text': 'Please help',
            'appreciation_text': 'I love you',
        }
        serializer = serializers.EmotionalNeedStateSerializer(
            data=data,
            context={'request': MockContext(self.user)})

        self.assertFalse(serializer.is_valid(raise_exception=False))
        self.assertEqual(
            serializer.errors,
            {'value_abs': [drf_exceptions.ErrorDetail(string='This field is required.', code='required')]}
        )
