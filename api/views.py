from rest_framework import generics
from smarttm_web.models import Participation
from smarttm_web.serializers import ParticipationSerializer


class ListParticipationsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer