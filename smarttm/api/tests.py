from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ..smarttm_web.models import Participation
from ..smarttm_web.serializers import ParticipationSerializer
 
# tests for views
 

class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_participation(title="", artist=""):
        if title != "" and artist != "":
            Participation.objects.create(title=title, artist=artist)

    def setUp(self):
        # add test data
        self.create_participation("like glue", "sean paul")
        self.create_participation("simple participation", "konshens")
        self.create_participation("love is wicked", "brick and lace")
        self.create_participation("jam rock", "damien marley")


class GetAllParticipationsTest(BaseViewTest):

    def test_get_all_participations(self):
        """
        This test ensures that all participations added in the setUp method
        exist when we make a GET request to the participations/ endpoint
        """
        # hit the API endpoint
        response = self.client.get(
            reverse("participations-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Participation.objects.all()
        serialized = ParticipationSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)