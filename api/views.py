from rest_framework import generics
from smarttm_web.models import Participation, Participation_Type, Club, Member, User, Meeting, Attendance
from smarttm_web.serializers import ParticipationSerializer, ParticipationTypeSerializer, ClubSerializer, \
    UserSerializer, MeetingSerializer, ParticipationSerializerForCat, MemberSerializer
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework import permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from datetime import datetime
import pdb


class ListParticipationsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer



#OPTIMIZED
#get participation types list
class ParticipationTypesList(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = Participation_Type.objects.all()
    serializer_class = ParticipationTypeSerializer

#OPTIMIZED
#get clubs of a user
class ClubListByUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request,  user_pk, format=None):
        memberships = Member.objects.filter(user__id = user_pk)
        clubs = []
        for member in memberships:
            clubs.append(member.club)
        serializer = ClubSerializer(clubs, many = True)
        return Response(serializer.data)

# OPTIMIZED
#get members of a club
class UserListByClub(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request,  club_pk, format=None):


        members = Member.objects.filter(club__id = club_pk, status = 1)
        serializer = MemberSerializer(members, many = True)
        return Response(serializer.data)


#OPTIMIZED
#get meeting for a particular day
class MeetingDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def meeting_create(self, club_id, meeting_date, created_date, updated_date):
        meeting = Meeting(club_id=club_id, meeting_date=meeting_date, created_date=timezone.now().date(),
                                 updated_date=timezone.now().date())
        meeting.save()
        return meeting

    def get(self, request,  club_pk, year, month, day):
        try:

            meeting_date = datetime(year=year, month=month, day=day)
            meeting = Meeting.objects.get(club__id = club_pk, meeting_date = meeting_date )
        except Meeting.DoesNotExist:
            meeting = self.meeting_create(club_id = club_pk, meeting_date = meeting_date, created_date = timezone.now(), updated_date = timezone.now())
        serializer = MeetingSerializer(meeting)
        return Response(serializer.data)


#OPTIMIZED
#get participation in a meeting of a member
class ParticipationDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def participation_create(self, meeting, member, participation_type, created_date, updated_date):

        participation = Participation(meeting=meeting, member=member, participation_type=participation_type,
                             created_date=timezone.now(), updated_date=timezone.now())
        participation.save()
        return participation

    def get(self, request,  meeting_pk, member_pk, participationtype_pk):

        try:
            participation = Participation.objects.get(meeting__id = meeting_pk, member__id = member_pk, participation_type__id = participationtype_pk)
        except:
            participation = self.participation_create(meeting_id = meeting_pk, member_id = member_pk, participation_type_id = participationtype_pk, created_date = timezone.now(), updated_date = timezone.now())

        serializer = ParticipationSerializer(participation)
        return Response(serializer.data)


#OPTIMIZED
class ParticipationListRoles(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, validated_data, meeting_pk, role_type, request):
        meeting = Meeting.objects.get(pk = meeting_pk)
        if not Member.objects.filter(club__id = meeting.club_id, user=request.user, active=True):
            raise PermissionDenied
        participation_list = []
        for item in validated_data:
            if role_type == 'timer':
                defaults = {'time_seconds': item.get('time_seconds', None)}
            elif role_type == 'ahcounter':
                defaults = {'ah_count': item.get('ah_count', None)}
            elif role_type == 'votecounter':
                defaults = {'vote_count': item.get('vote_count', None)}
            elif role_type == 'grammarian':
                defaults = {'grammar_good': item.get('grammar_good', None),
                            'grammar_bad': item.get('grammar_bad', None),
                            'grammar_remarks': item.get('grammar_remarks', None)}
            else:
                raise Http404
            participation, created = Participation.objects.update_or_create(
                club_id = meeting.club_id,
                meeting_id = meeting_pk,
                participation_type_id = item.get('participation_type', None),
                member_id = item.get('member', None),
                defaults = defaults

            )

            participation.created_by = self.request.user if created else participation.created_by
            participation.updated_by = self.request.user
            participation.created_date = timezone.now() if created else participation.created_date
            participation.updated_date = timezone.now()

            participation_list.append(participation)
        Participation.objects.bulk_update(participation_list, ['created_by', 'updated_by', 'created_date', 'updated_date']+list(defaults.keys()))
        return participation_list

    def post(self, request, role_type, meeting_pk, format = None):


        serializer = ParticipationSerializer(data = request.data, many =True)
        if serializer.is_valid():
            participation_list = self.create(serializer.data, meeting_pk, role_type, request)
            serializer = ParticipationSerializer(participation_list, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#OPTIMIZED
class CatBasedParticipations(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get_roles(self, cat):
        if cat.lower() == 'basic':
            roles = Participation_Type.objects.filter(category = 'Role-Basic')
        elif cat.lower() == 'advanced':
            roles = Participation_Type.objects.filter(category = 'Role-Advanced')
        else:
            raise Http404
        return roles

    def get_participations(self, role, member_pk):

        participations = Participation.objects.filter(participation_type = role, member__id = member_pk)
        return  participations

    def get(self, request, member_pk, cat):

        roles = self.get_roles(cat)
        participations = []
        for role in roles:
            temp_participations = self.get_participations(role, member_pk)
            for participation in temp_participations:
                participations.append(participation)



        serializer = ParticipationSerializerForCat(participations, many=True)
        return Response(serializer.data)

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'name': user.full_name
        })


class ToggleAttendance(APIView):

    def get(self, request, attendance_id):
        try:

            att = Attendance.objects.get(pk = attendance_id)
            att.present = True if att.present is False else False
            att.save()
            return Response({
                'status': 'success',
                'present': att.present
            })
        except:
            return Response({
                'status': 'failed'
            })


class ParticipationObj(APIView):
    def delete(self, request, participation_id):
        try:
            part = Participation.objects.get(pk=participation_id).delete()
            return Response({
                'status': 'success'
            })
        except:
            return Response({
                'status': 'failed'
            })