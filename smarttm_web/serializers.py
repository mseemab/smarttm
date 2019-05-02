from rest_framework import serializers
from .models import Participation


class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = ('meeting', 'participation_type', 'user')