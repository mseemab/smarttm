from rest_framework import generics
from smarttm_web.models import Participation, Participation_Type, Club, Member, User, Meeting
from smarttm_web.serializers import ParticipationSerializer, ParticipationTypeSerializer, ClubSerializer, \
    UserSerializer, MeetingSerializer, ParticipationSerializerForCat
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework import permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied

class ListParticipationsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer

#get participation types list
class ParticipationTypesList(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = Participation_Type.objects.all()
    serializer_class = ParticipationTypeSerializer

#get clubs of a user
class ClubListByUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get_user_object(self, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            raise Http404
        return user
    def get(self, request,  user_pk, format=None):

        user = self.get_user_object(user_pk=user_pk)
        memberships = Member.objects.filter(user = user)
        clubs = []
        for member in memberships:
            clubs.append(member.club)
        serializer = ClubSerializer(clubs, many = True)
        return Response(serializer.data)

#get members of a club
class UserListByClub(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get_club_object(self, club_pk):
        try:
            club = Club.objects.get(pk=club_pk)
        except Club.DoesNotExist:
            raise Http404
        return club

    def get(self, request,  club_pk, format=None):

        club = self.get_club_object(club_pk)
        members = Member.objects.filter(club = club, status = 1)
        users = []
        for member in members:
            users.append(member.user)
        serializer = UserSerializer(users, many = True)
        return Response(serializer.data)

#get meeting for a particular day
class MeetingDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get_club_object(self, club_pk):
        try:
            club = Club.objects.get(pk=club_pk)
        except Club.DoesNotExist:
            raise Http404
        return club

    def meeting_create(self, club, meeting_date, created_date, updated_date):
        meeting = Meeting(club=club, meeting_date=meeting_date, created_date=timezone.now().date(),
                                 updated_date=timezone.now().date())
        meeting.save()
        return meeting

    def get(self, request,  club_pk, year, month, day):
        club = self.get_club_object(club_pk)
        try:
            from datetime import datetime
            meeting_date = datetime(year=year, month=month, day=day)
            meeting = Meeting.objects.get(club = club, meeting_date = meeting_date )
        except Meeting.DoesNotExist:
            meeting = self.meeting_create(club = club, meeting_date = meeting_date, created_date = timezone.now(), updated_date = timezone.now())
        serializer = MeetingSerializer(meeting)
        return Response(serializer.data)

#get participation in a meeting of a member
class ParticipationDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get_meeting_object(self, meeting_pk):
        try:
            meeting = Meeting.objects.get(pk=meeting_pk)
        except Meeting.DoesNotExist:
            raise Http404
        return meeting

    def get_user_object(self, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            raise Http404
        return user

    def get_participationtype_object(self, participationtype_pk):
        try:
            participationtype = Participation_Type.objects.get(pk=participationtype_pk)
        except Participation_Type.DoesNotExist:
            raise Http404
        return participationtype

    def participation_create(self, meeting, user, participation_type, created_date, updated_date):

        participation = Participation(meeting=meeting, user=user, participation_type=participation_type,
                             created_date=timezone.now(), updated_date=timezone.now())
        participation.save()
        return participation

    def get(self, request,  meeting_pk, user_pk, participationtype_pk):

        meeting = self.get_meeting_object(meeting_pk)
        user = self.get_user_object(user_pk)
        participation_type = self.get_participationtype_object(participationtype_pk)
        try:
            participation = Participation.objects.get(meeting = meeting, user = user, participation_type = participation_type)
        except:
            participation = self.participation_create(meeting = meeting, user = user, participation_type = participation_type, created_date = timezone.now(), updated_date = timezone.now())

        serializer = ParticipationSerializer(participation)
        return Response(serializer.data)

class ParticipationList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, validated_data):
        import pdb
        pdb.set_trace()
        participation_list = []
        for item in validated_data:
            participation, created = Participation.objects.update_or_create(
                meeting = Meeting.objects.get(pk = item.get('meeting', None)),
                participation_type = Participation_Type.objects.get(pk = item.get('participation_type', None)),
                user = User.objects.get(pk = item.get('user', None)),
                defaults = {'time_seconds': item.get('time_seconds', None)}

            )
            participation.created_by = self.request.user if created else participation.created_by
            participation.updated_by = self.request.user
            participation.created_date = timezone.now() if created else participation.created_date
            participation.updated_date = timezone.now()

            participation_list.append(participation)

        return participation_list

    def get_meeting_object(self, meeting_pk):
        try:
            meeting = Meeting.objects.get(pk=meeting_pk)
        except Meeting.DoesNotExist:
            raise Http404
        return meeting

    def get(self,  request, meeting_pk, format = None):

        meeting = self.get_meeting_object(meeting_pk)
        participationlist = meeting.participation_set.all()
        serializer = ParticipationSerializer(participationlist, many = True)
        return Response(serializer.data)

    def post(self, request, meeting_pk, format = None):
        serializer = ParticipationSerializer(data = request.data, many =True)
        if serializer.is_valid():
            serializer.save(created_by=self.request.user, updated_by=self.request.user, created_date=timezone.now(),
                            updated_date = timezone.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ParticipationListRoles(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, validated_data, meeting_pk, role_type, request):
        club = Meeting.objects.get(pk = meeting_pk).club
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



            if not Member.objects.filter(club = club, user = request.user, active = True):
                raise PermissionDenied

            participation, created = Participation.objects.update_or_create(
                meeting_id = meeting_pk,
                participation_type = Participation_Type.objects.get(pk = item.get('participation_type', None)),
                user = User.objects.get(pk = item.get('user', None)),
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
        print (request.user)

        serializer = ParticipationSerializer(data = request.data, many =True)
        if serializer.is_valid():
            participation_list = self.create(serializer.data, meeting_pk, role_type, request)
            serializer = ParticipationSerializer(participation_list, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CatBasedParticipations(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get_member_object(self, member_pk):
        try:
            member = Member.objects.get(pk = member_pk)
        except:
            raise Http404
        return member

    def get_roles(self, cat):
        if cat == 'basic':
            roles = Participation_Type.objects.filter(category = 'Role-Basic')
        elif cat == 'advanced':
            roles = Participation_Type.objects.filter(category = 'Role-Advanced')
        else:
            raise Http404
        return roles

    def get_participations(self, role, member):

        participations = Participation.objects.filter(participation_type = role, member = member)
        return  participations

    def get(self, request, member_pk, cat):

        member = self.get_member_object(member_pk)
        roles = self.get_roles(cat)
        participations = []
        for role in roles:
            temp_participations = self.get_participations(role, member)
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


