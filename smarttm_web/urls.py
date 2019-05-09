from django.urls import path
from . import views
from django.urls import path, include # new
from smarttm_web import meeting_views
urlpatterns = [
   path('meeting/<int:meeting_id>/', meeting_views.meeting, name = 'meeting_detail'),
   path('summary/', views.summary, name = 'ranking_summary'),
   path('ManageClub/', views.club_management, name = 'manage_club'),
   path('LoginUser/', views.login_user, name = 'LoginUser'),
   path('register/', views.register , name = 'register'),
   path('ClubMeetings/', meeting_views.meetings_view, name = 'meeting_summary'),
   path('MySpace', views.my_space , name = 'register'),
   path('SetClub/<int:club_id>/', views.set_club, name = 'SetClub'),
   path('ImportMembers/', views.ImportMembers, name = 'import_members'),
]


# urlpatterns = [
#     path('', ListParticipationsView.as_view(), name="participations-all"),
#     path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
# ]