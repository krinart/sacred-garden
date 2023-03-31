from django.test import TestCase

from sacred_garden import models
from sacred_garden import serializers


class TestTest(TestCase):

    def test_test(self):
        user = models.User.objects.create()
        eneed1 = models.EmotionalNeed.objects.create(user=user, name='Hug')
        models.create_emotional_need_value(user, eneed1, 1)
        models.create_emotional_need_value(user, eneed1, 2)

        eneed2 = models.EmotionalNeed.objects.create(user=user, name='Kiss')
        models.create_emotional_need_value(user, eneed2, 3)
        models.create_emotional_need_value(user, eneed2, 4)

        with self.assertNumQueries(2) as c:
            emotional_needs = models.get_emotional_needs_with_prefetched_current_values(user=user)

            serializer = serializers.EmotionalNeedSerializer(instance=emotional_needs, many=True)
            data = serializer.data

            self.assertEqual(len(data), 2)

            del data[0]['current_value']['created_at']
            del data[1]['current_value']['created_at']

            eneed1_data = {
                'id': eneed1.id,
                'name': 'Hug',
                'current_value': {'value': 2}
            }
            self.assertDictEqual(data[0], eneed1_data)

            eneed2_data = {
                'id': eneed2.id,
                'name': 'Kiss',
                'current_value': {'value': 4}
            }
            self.assertDictEqual(data[1], eneed2_data)
