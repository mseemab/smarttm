from django.urls import path
from . import views
from django.urls import path, include # new
from smarttm_web import meeting_views
urlpatterns = [
    path('clubs/<int:club_id>/meetings/<int:meeting_id>/', meeting_views.meeting, name = 'meeting_detail'),
    path('', views.index, name = 'index'),
    path('clubs/<int:club_id>/members/', views.club_management, name = 'club_members'),
    path('clubs/<int:club_id>/rankings/', views.club_ranking, name = 'club_rankings'),
    path('clubs/<int:club_id>/members/<int:member_id>/', views.member_detail, name = 'member_detail'),
    path('accounts/login/', views.login_user, name = 'LoginUser'),
    path('accounts/register/', views.register , name = 'register'),
    path('clubs/<int:club_id>/meetings/', meeting_views.meetings_view, name = 'club_meetings'),
    # path('my-space', views.my_space , name = 'my_space'),
    path('set-club/<int:club_id>/', views.set_club, name = 'set_club'),
    path('clubs/<int:club_id>/members/import/', views.import_members, name = 'import_members'),
    path('meetings/create/', meeting_views.add_meeting, name = 'add_meeting'),
    path('meetings/participations/import/', meeting_views.import_meeting_data, name = 'import_meeting_data'),
    path('clubs/<int:club_id>/participationemail', views.send_participation_email, name = 'send_participation_email'),
]


# urlpatterns = [
#     path('', ListParticipationsView.as_view(), name="participations-all"),
#     path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
# ]