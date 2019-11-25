from django.urls import path
from . import views
from django.urls import path, include # new
from smarttm_web import meeting_views
urlpatterns = [
   path('meetings/<int:meeting_id>/', meeting_views.meeting, name = 'meeting_detail'),
   path('', views.index, name = 'index'),
   path('summary/', views.summary, name = 'ranking_summary'),
   path('club/members/', views.club_management, name = 'manage_club'),
   path('clubs/<int:club_id>/rankings/', views.club_ranking, name = 'club_rankings'),
   path('clubs/<int:club_id>/members/<int:member_id>/', views.member_detail, name = 'member_detail'),
   path('accounts/login/', views.login_user, name = 'LoginUser'),
   path('accounts/register/', views.register , name = 'register'),
   path('meetings/', meeting_views.meetings_view, name = 'meeting_summary'),
   # path('my-space', views.my_space , name = 'my_space'),
   path('set-club/<int:club_id>/', views.set_club, name = 'SetClub'),
   path('club/members/import/', views.ImportMembers, name = 'import_members'),
   path('meetings/create/', meeting_views.add_meeting, name = 'add_meeting'),
   path('meetings/participations/import/', meeting_views.import_meeting_data, name = 'import_meeting_data'),
   path('club/<int:club_id>/participationemail', views.send_participation_email, name = 'send_participation_email'),
]


# urlpatterns = [
#     path('', ListParticipationsView.as_view(), name="participations-all"),
#     path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
# ]