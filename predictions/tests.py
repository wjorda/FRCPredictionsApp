from django.test import TestCase, Client


# Create your tests here.
class TestWebhooks(TestCase):
    def setUp(self):
        """initialize the Django test client"""
        self.c = Client()

    def testWebhook(self):
        content = """
        {
          "message_data": {
            "event_name": "New England FRC Region Championship",
            "match": {
              "comp_level": "f",
              "match_number": 1,
              "videos": [],
              "time_string": "3:18 PM",
              "set_number": 1,
              "key": "2014necmp_f1m1",
              "time": 1397330280,
              "score_breakdown": null,
              "alliances": {
                "blue": {
                  "score": 154,
                  "teams": [
                    "frc177",
                    "frc230",
                    "frc4055"
                  ]
                },
                "red": {
                  "score": 78,
                  "teams": [
                    "frc195",
                    "frc558",
                    "frc5122"
                  ]
                }
              },
              "event_key": "2014necmp"
            }
          },
          "message_type": "match_score"
        }
        """
        response = self.client.post('/webhook/', content, 'text/json', **{'X-TBA-Checksum': "3345353"})
        self.assertEqual(response.status_code, 200)
