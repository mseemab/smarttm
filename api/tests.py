from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from smarttm_web.models import Participation, Meeting, Participation_Type, Club, User, Member
from smarttm_web.serializers import ParticipationSerializer
from django.utils import timezone
# tests for views
 

class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_participation(meeting, participation_type, user):

        return Participation.objects.create(meeting=meeting, participation_type=participation_type, user=user)

    @staticmethod
    def create_meeting(meeting_date, club):
        return Meeting.objects.create(meeting_date = meeting_date, club = club)

    @staticmethod
    def create_club(name):
        return Club.objects.create(name=name)

    @staticmethod
    def create_participation_type(name):
        return Participation_Type.objects.create(name=name)

    @staticmethod
    def create_user(email, password):
        return User.objects.create_user(email=email, password=password)


    def setUp(self):
        # add test data
        user1 = self.create_user('a@smarttm.com', 'asdasd32423')
        user2 = self.create_user('ab@smarttm.com', 'asdasd32423')
        user3 = self.create_user('abc@smarttm.com', 'asdasd32423')
        user4 = self.create_user('abcd@smarttm.com', 'asdasd32423')

        club1 = self.create_club('Islamabad')
        club2 = self.create_club('Rawalpindi')
        club3 = self.create_club('Lahore')
        club4 = self.create_club('Karachi')

        meeting1 = self.create_meeting(timezone.now(), club1)
        meeting2 = self.create_meeting(timezone.now(), club2)
        meeting3 = self.create_meeting(timezone.now(), club3)
        meeting4 = self.create_meeting(timezone.now(), club4)

        part_type1 = self.create_participation_type('tt')
        part_type2 = self.create_participation_type('speech')
        part_type3 = self.create_participation_type('evaluation')
        part_type4 = self.create_participation_type('timer')

        self.create_participation(meeting1, part_type1, user1)
        self.create_participation(meeting2, part_type2, user2)
        self.create_participation(meeting3, part_type3, user3)
        self.create_participation(meeting4, part_type4, user4)


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