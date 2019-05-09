from django.shortcuts import render
from smarttm_web.models import Meeting, Club, Participation_Type, Participation, Meeting_Summary
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required()
def meetings_view(request):
    club_key = request.session['SelectedClub'][0]
    meetings = Meeting.objects.filter(club__id = club_key)
    participation_types = Participation_Type.objects.all()
    part_type_speech = participation_types.filter(category = 'Speech').values_list('id', flat = True)
    part_type_tt = participation_types.filter(name = 'Table Topic')
    part_type_prep = participation_types.filter(name='Prepared Speech')
    participations = Participation.objects.filter(club__id = request.session['SelectedClub'][0])
    meeting_summary = []
    for meeting in meetings:
        meeting_date = meeting.meeting_date
        speech_count = participations.filter(meeting__id = meeting.pk)
