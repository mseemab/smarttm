from django.shortcuts import render
from smarttm_web.models import Meeting, Club, Participation_Type, Participation, Meeting_Summary, Attendance, Member
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.db.models import Q
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
        prep_speech_count = participations.filter(meeting=meeting, participation_type=part_type_prep).count()
        present_count = Attendance.objects.filter(meeting = meeting, present = True).count()
        absent_count = Attendance.objects.filter(meeting=meeting, present = False).count()
        meeting_summary.append(Meeting_Summary(meeting = meeting, speech_count = speech_count,
                                               tt_count = tt_count, prep_speech_count = prep_speech_count,
                                               members_present_count = present_count, members_absent_count = absent_count))

    return render(request, 'meetings.html', {'summ_set': meeting_summary})

@login_required()
def meeting(request, meeting_id):
    meeting = Meeting.objects.get(pk=meeting_id)

    # get participation_types
    part_types = Participation_Type.objects.all()
    role_basic = part_types.filter(category='Role-Basic')
    role_advanced = part_types.filter(category='Role-Advanced')
    speech_types = part_types.filter(category='Speech')
    attendance = Attendance.objects.filter(meeting_id = meeting_id)
    # get meeting participations
    meeting_participations = Participation.objects.filter(meeting__id=meeting_id)
    role_basic_part = meeting_participations.filter(participation_type__in=role_basic)
    role_advanced_part = meeting_participations.filter(participation_type__in=role_advanced)
    speech_part = meeting_participations.filter(participation_type__in=speech_types)

    return render(request, 'meetingdetail.html', {'meeting': meeting, 'role_basic_part': role_basic_part,
                                                  'role_advanced_part': role_advanced_part, 'speech_part': speech_part,
                                                  'attendance': attendance, 'part_types': part_types})

@login_required()
def add_meeting(request):
    if request.method == 'POST':

        club_key = request.session['SelectedClub'][0]
        meeting_date = request.POST.get('meeting_date')
        meeting_no = request.POST.get('meeting_no')
        #check if meeting already exists
        ex_meeting_count = Meeting.objects.filter(Q(meeting_date = meeting_date) | Q(meeting_no = meeting_no), club_id = club_key ).count()
        if ex_meeting_count > 0:
            messages.warning(request, 'Meeting for %s or Meeting Number %s already exists' % (meeting_date, meeting_no))
            response = redirect("meeting_summary")
            return response
        else:
            new_meeting = Meeting.objects.create(club_id = club_key, meeting_date = meeting_date, meeting_no = meeting_no)
            new_meeting.save()
            messages.success(request, 'Meeting for %s created successfully.' % meeting_date)
            club_members = Member.objects.filter(club_id = club_key, active = True)
            attendances = []
            #initiate attendances for the meeting
            for member in club_members:
                new_att = Attendance(meeting = new_meeting, member = member)
                attendances.append(new_att)
            Attendance.objects.bulk_create(attendances)
            response = redirect( "meeting_summary")
            return response

@login_required()
def import_meeting_data(request):
    header_list = ['Member ID', 'Member Name', 'Participation Type']
    if request.method == 'POST':
        import_file = request.FILES['importfile']
        try:
            data_df = pd.read_excel(import_file, sheet_name='Participation Data')
        except Exception as e:
            messages.error(request, "There was some error reading the imported file. Make sure there is a sheet named 'Participation Data' in it" )
            response = redirect('meeting_detail', meeting_id = request.POST.get('meeting_id'))
            return response

        if not set(header_list).issubset(set(data_df.columns.tolist())):
            messages.error(request,
                           "The file format is not correct.")
            response = redirect('meeting_detail', meeting_id=request.POST.get('meeting_id'))
            return response

        data_df = data_df.drop_duplicates(['Member ID', 'Participation Type'])
        meeting_id = request.POST.get('meeting_id')
        club_key = request.session['SelectedClub'][0]
        club_members = Member.objects.filter(club_id = club_key, active = True)
        parts = Participation.objects.filter(meeting_id = meeting_id)
        part_types = Participation_Type.objects.all()
        new_parts = []
        for index, row in data_df.iterrows():
            member_id = row['Member ID']
            part_type = part_types.filter(name = row['Participation Type'])
            if len(part_type) == 0:
                continue
            ex_parts = parts.filter(member_id = member_id, participation_type = part_type[0])
            if len(ex_parts) > 0:
                continue
            member = club_members.filter(pk = member_id)
            if len(member) == 0:
                continue

            part_new = Participation(meeting_id = meeting_id, member = member[0], participation_type = part_type[0], club_id = club_key)
            new_parts.append(part_new)
            att, created = Attendance.objects.update_or_create(member_id=member_id, meeting_id=meeting_id,
                                                               defaults={
                                                                   'present': True,
                                                               }
                                                               )

        Participation.objects.bulk_create(new_parts)
        messages.success(request,
                       "All matching records are successfully added.")
        response = redirect('meeting_detail', meeting_id=request.POST.get('meeting_id'))
        return response
