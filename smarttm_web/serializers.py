from rest_framework import serializers
from .models import Participation, User, Member, Club, Participation_Type, Meeting

class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = '__all__'



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk','full_name', 'email', 'status')


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ('pk','club', 'user')

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ('pk','name', 'club_number', 'address')

class ParticipationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation_Type
        fields = ('pk','name', 'category')


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ('pk','club', 'meeting_date')

class ParticipationSerializerForCat(serializers.ModelSerializer):
    participation_type = ParticipationTypeSerializer(read_only=True)
    meeting = MeetingSerializer(read_only=True)
    class Meta:
        model = Participation
        fields = ('participation_type', 'meeting')