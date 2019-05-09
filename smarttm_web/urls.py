from django.urls import path
from . import views
from django.urls import path, include # new

urlpatterns = [
   path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
   path('summary', views.summary, name = 'summary'),
   path('ManageClub', views.club_management, name = 'ManageClub'),
   path('LoginUser', views.login_user, name = 'LoginUser'),
   path('register', views.register , name = 'register'),

   path('SetClub/<int:club_id>/', views.set_club, name = 'SetClub'),
   path('ImportMembers', views.ImportMembers, name = 'summary'),
]


# urlpatterns = [
#     path('', ListParticipationsView.as_view(), name="participations-all"),
#     path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
# ]