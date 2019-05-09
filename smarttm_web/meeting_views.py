from django.shortcuts import render
from smarttm_web.models import Meeting, Club, Participation_Type, Participation, Meeting_Summary
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import pdb

@login_required()
def meetings_view(request):
    club_key = request.session['SelectedClub'][0]
    meetings = Meeting.objects.filter(club__id = club_key)
    participation_types = Participation_Type.objects.all()
    part_type_speech = set(participation_types.filter(category = 'Speech').values_list('id', flat = True))
    part_type_tt = participation_types.get(name = 'Table Topic')
    part_type_prep = participation_types.get(name='Prepared Speech')
    participations = Participation.objects.filter(club__id = request.session['SelectedClub'][0])
    meeting_summary = []

    for meeting in meetings:
        meeting_date = meeting.meeting_date
        speech_count = participations.filter(meeting = meeting, participation_type__id__in = part_type_speech).count()
        tt_count = participations.filter(meeting = meeting, participation_type = part_type_tt).count()
        prep_speech_count = participations.filter(meeting=meeting, participation_type=part_type_tt).count()
        meeting_summary.append(Meeting_Summary(meeting = meeting, speech_count = speech_count,
                                               tt_count = tt_count, prep_speech_count = prep_speech_count))

    return render(request, 'meetings.html', {'summ_set': meeting_summary})

@login_required()
def meeting(request, meeting_id):
    meeting = Meeting.objects.get(pk=meeting_id)

    # get participation_types
    part_types = Participation_Type.objects.all()
    role_basic = part_types.filter(category='Role-Basic')
    role_advanced = part_types.filter(category='Role-Advanced')
    speech_types = part_types.filter(category='Speech')

    # get meeting participations
    meeting_participations = Participation.objects.filter(meeting__id=meeting_id)
    role_basic_part = meeting_participations.filter(participation_type__in=role_basic)
    role_advanced_part = meeting_participations.filter(participation_type__in=role_advanced)
    speech_part = meeting_participations.filter(participation_type__in=speech_types)

    return render(request, 'meetingdetail.html', {'meeting': meeting, 'role_basic_part': role_basic_part,
                                                  'role_advanced_part': role_advanced_part, 'speech_part': speech_part })