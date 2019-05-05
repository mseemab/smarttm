from django.urls import path
from . import views
from api.views import ListParticipationsView

urlpatterns = [
   path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
   path('summary/<int:club_key>/', views.summary, name = 'summary'),
   path('ManageClub', views.club_management, name = 'ManageClub')
]


# urlpatterns = [
#     path('', ListParticipationsView.as_view(), name="participations-all"),
#     path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
# ]