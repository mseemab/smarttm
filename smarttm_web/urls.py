from django.urls import path
from . import views


urlpatterns = [
   path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
]


# urlpatterns = [
#     path('', ListParticipationsView.as_view(), name="participations-all"),
#     path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
# ]