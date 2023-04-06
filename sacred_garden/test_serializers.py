from django.test import TestCase

from sacred_garden import models
from sacred_garden import serializers


class TestTest(TestCase):

    def test_test(self):
        user = models.User.objects.create()
        eneed1 = models.EmotionalNeed.objects.create(user=user, name='Hug')
        models.create_emotional_need_state(user, eneed1, 1, 0, "", "")
        ens1 = models.create_emotional_need_state(user, eneed1, 2, 1, "", "")

        eneed2 = models.EmotionalNeed.objects.create(user=user, name='Kiss')
        models.create_emotional_need_state(user, eneed2, 3, 0, "", "")
        ens2 = models.create_emotional_need_state(user, eneed2, 4, 1, "", "")

        with self.assertNumQueries(2) as c:
            emotional_needs = models.get_emotional_needs_with_prefetched_current_values(user=user)

            serializer = serializers.EmotionalNeedSerializer(instance=emotional_needs, many=True)
            data = serializer.data

            self.assertEqual(len(data), 2)

            del data[0]['current_status']['created_at']
            del data[1]['current_status']['created_at']

            eneed1_data = {
                'id': eneed1.id,
                'name': 'Hug',
                'current_status': {
                    'id': ens1.id,
                    'emotional_need_id': eneed1.id,
                    'status': 2,
                    'trend': 1,
                    'text': '',
                    'appreciation_text': '',

                }
            }
            self.assertDictEqual(data[0], eneed1_data)

            eneed2_data = {
                'id': eneed2.id,
                'name': 'Kiss',
                'current_status': {
                    'id': ens2.id,
                    'emotional_need_id': eneed2.id,
                    'status': 4,
                    'trend': 1,
                    'text': '',
                    'appreciation_text': '',
                }
            }
            self.assertDictEqual(data[1], eneed2_data)
