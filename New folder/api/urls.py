from django.contrib import admin
from django.urls import path, include, re_path
from api.views import ParticipationTypesList, ClubListByUser, UserListByClub, MeetingDetail, \
    ParticipationDetail, CustomAuthToken, ParticipationListRoles, CatBasedParticipations, ToggleAttendance
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authtoken.views import obtain_auth_token


schema_view = get_schema_view(
   openapi.Info(
      title="SMARTTM API",
      default_version='v1',
      description="SMARTTM API For Usage",
      terms_of_service="https://www.google.com/policies/terms/",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    #re_path('participations', ListParticipationsView.as_view(), name="participations_all"),
    path('getparticipationtypes', ParticipationTypesList.as_view(), name="participation_types_all"),
    path('getuserclubs/<int:user_pk>/', ClubListByUser.as_view(), name="get_user_clubs"),
    path('getclubmembers/<int:club_pk>/', UserListByClub.as_view(), name="get_club_members"),
    path('getmeeting/<int:club_pk>/<int:year>/<int:month>/<int:day>/', MeetingDetail.as_view(), name="get_meeting"),
    path('getparticipation/<int:meeting_pk>/<int:user_pk>/<int:participationtype_pk>/', ParticipationDetail.as_view(), name="get_participation"),
    path('participationlistupdate/<int:meeting_pk>/<str:role_type>/', ParticipationListRoles.as_view(), name="participation_list_update"),
    path('getcatparticipations/<int:member_pk>/<str:cat>/', CatBasedParticipations.as_view(), name = "get_cat_participations"),
    path('toggleattendance/<int:attendance_id>/', ToggleAttendance.as_view(), name = "toggle_attendance"),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger'),
    path('api-token-auth/', CustomAuthToken.as_view())
]