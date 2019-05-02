from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('meeting/<int:meeting_id>/', views.meeting, name = 'meeting'),
]