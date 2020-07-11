from django.urls import path
from . import views
from django.urls import path, include # new
from smarttm_web import meeting_views, request_views
urlpatterns = [
    path('', views.index, name = 'index'),
    path('accounts/login/', views.login_user, name = 'login_user'),
    path('accounts/register/', views.register , name = 'register'),

    path('clubs/<int:club_id>/meetings/', meeting_views.meetings_view, name = 'club_meetings'),
    path('clubs/<int:club_id>/meetings/<int:meeting_id>/', meeting_views.meeting, name = 'meeting_detail'),
    path('clubs/<int:club_id>/meetings/create/', meeting_views.add_meeting, name='add_meeting'),
    path('clubs/<int:club_id>/meetings/participations/import/', meeting_views.import_meeting_data, name='import_meeting_data'),

    path('clubs/<int:club_id>/members/', views.club_management, name = 'club_members'),
    path('clubs/<int:club_id>/members/<int:member_id>/', views.member_detail, name='member_detail'),
    path('clubs/<int:club_id>/members/import/', views.import_members, name = 'import_members'),

    path('clubs/<int:club_id>/requests', request_views.requests_view, name='club_requests'),
    path('clubs/<int:club_id>/requests/pending', request_views.pending_requests_view, name = 'pending_requests'),
    path('clubs/<int:club_id>/requests/my', request_views.my_requests_view, name = 'user_requests'),
    path('clubs/<int:club_id>/requests/new', request_views.requests_new, name = 'club_requests_new'),

    path('clubs/<int:club_id>/rankings/', views.club_ranking, name = 'club_rankings'),
    path('clubs/<int:club_id>/participationemail', views.send_participation_email, name = 'send_participation_email'),
    path('set-club/<int:club_id>/', views.set_club, name = 'set_club'),
]


# urlpatterns = [
#     path('', ListParticipationsView.as_view(), name="participations-all"),
#     path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
# ]