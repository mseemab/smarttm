from django.shortcuts import render
from django.urls import reverse
from smarttm_web.models import Meeting, User, Member, Club, Participation, Summary, Participation_Type, Attendance
from django.shortcuts import render_to_response
import pdb
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage
import pandas as pd
from django.utils import timezone
from datetime import date
from django.db.models import Avg
import math
from django.contrib.auth.decorators import login_required
from smarttm_web.forms import UserForm
from django.core.mail import send_mail
from django.template import loader
import threading
from .decorators import query_debugger, request_passes_test
from datetime import datetime
from smarttm_web.request_tests import user_is_ec, user_is_member
# Create your views here.


def login_user(request):
    
    if request.method == 'POST':

        username = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
               # create sessions.
                # Get user clubs
                
                clubs = user.get_clubs()
                if not len(clubs) == 0:
                    login(request, user)
                    UserClubData = []
                    for club in clubs:
                        UserClubData.append([club.pk, club.name, user.is_ec(club)])

                    request.session['UserClubs'] = UserClubData

                    request.session['SelectedClub'] = UserClubData[0]

                    request.session.modified = True
                
                    return redirect(reverse('index'))
                else:
                    messages.warning(request, 'You are not a member of any Club. Please join a club to use SMARTTM.')
                    return redirect('login_user')
            else:
                messages.warning(request, 'Your account is not activated') 
                response = redirect('login_user')
                return response
        else:
           messages.warning(request, 'Invalid email/password.') 
           response = redirect('login_user')
           return response
    else:
        
        return render(request, 'registration/login.html' )


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
        else:
            print(user_form.errors)
            registered = True
    else:
        user_form = UserForm()
    return render(request, 'registration/register.html', {'user_form': user_form, 'registered': registered})


@login_required()
def index(request):

    return redirect(reverse('club_rankings', args=(request.session['SelectedClub'][0],)))


@login_required()
@request_passes_test(user_is_member)
def set_club(request, club_id):
    user = request.user
    club = Club.objects.get(id=club_id)
    request.session['SelectedClub'] = [club.pk,club.name,user.is_ec(club)]
    request.session.modified = True
    return redirect(reverse('index'))


@login_required()
@request_passes_test(user_is_ec)
def import_members(request, club_id):
    
    club_obj = Club.objects.get(pk=club_id)
    if request.method == 'POST':
        import_file = request.FILES['importfile']
        try:
            club_obj.import_members(import_file)
            messages.success(request, 'Members imported.')
        except Exception as e:
            messages.warning(request, repr(e))
    return redirect(request.META.get('HTTP_REFERER'))


@login_required()
@request_passes_test(user_is_member)
def club_ranking(request, club_id):

    if request.method == 'POST':
        from_date = request.POST.get("StartDate", "")
        to_date = request.POST.get("EndDate", "")
    else:
        if datetime.today().month > 6 and datetime.today().month <=12:
            from_year = datetime.today().year
        else:
            from_year = datetime.today().year - 1
        from_date = str(from_year)+ '-07-01'
        to_date = datetime.today().strftime("%Y-%m-%d")

    club_obj = Club.objects.get(pk=club_id)
    club_members = club_obj.members.filter(active=True, paid_status=True)

    club_meets = club_obj.meeting_set.filter(meeting_date__range=(from_date, to_date))
    partication_set = Participation.objects.none()
    attendance_set = Attendance.objects.none()
    for meet in club_meets:
        partication_set = partication_set | meet.participation_set.all()
        attendance_set = attendance_set | meet.attendance_set.all()

    category_adv = Participation_Type.objects.filter(category='Role-Advanced')
    category_basic = Participation_Type.objects.filter(category='Role-Basic')
    tt_type = Participation_Type.objects.get(name='Table Topic')
    speech_type = Participation_Type.objects.get(name='Prepared Speech')
    eval_type = Participation_Type.objects.get(name='Evaluation')
    ge_type = Participation_Type.objects.get(name='General Evaluator')
    ttm_type = Participation_Type.objects.get(name='Table Topics Master')
    toe_type = Participation_Type.objects.get(name='Toastmaster of the Evening')

    summ = []

    club_member_ids = [member.pk for member in club_members]
    latest_absents = Attendance.get_latest_absents(club_member_ids)

    latest_absents_dict = {}
    for absent in latest_absents:
        latest_absents_dict[absent.member_id] = absent.count_absents

    participation_count = Participation.get_participation_count(club_member_ids, from_date, to_date)
    part_percent_dict = {}
    for part_count in participation_count:
        part_percent_dict[part_count.id] = math.ceil(
            (part_count.TotalParticipations / part_count.TotalAttendance) * 100) \
            if part_count.TotalAttendance != 0 else 0
    for club_mem in club_members:
        sum_obj = Summary()
        sum_obj.member = club_mem
        sum_obj.tt_count = partication_set.filter(member=club_mem, participation_type=tt_type).count()
        sum_obj.speeches_count = partication_set.filter(member=club_mem, participation_type=speech_type).count()
        sum_obj.evaluation_count = partication_set.filter(member=club_mem, participation_type=eval_type).count()
        sum_obj.ttm_count = partication_set.filter(member=club_mem, participation_type=ttm_type).count()
        sum_obj.ge_count = partication_set.filter(member=club_mem, participation_type=ge_type).count()
        sum_obj.toe_count = partication_set.filter(member=club_mem, participation_type=toe_type).count()
        sum_obj.adv_role_count = partication_set.filter(member=club_mem, participation_type__in=category_adv).count()
        sum_obj.basic_role_count = partication_set.filter(member=club_mem, participation_type__in=category_basic).count()

        presents = attendance_set.filter(member=club_mem, present=True).count()
        absents = attendance_set.filter(member=club_mem, present=False).count()

        sum_obj.attendance_percent = math.ceil(
            (presents / (presents + absents)) * 100) if presents + absents != 0 else 0
        try:
            sum_obj.last_absents = latest_absents_dict[club_mem.id]
        except:
            sum_obj.last_absents = 0
        try:
            sum_obj.part_percent = part_percent_dict[club_mem.id]
        except:
            sum_obj.sum_obj.part_percent = 0


        summ.append(sum_obj)

    # add rankings
    for i in range(len(summ) - 1, 0, -1):
        for j in range(i):
            if (summ[j].part_percent < summ[j + 1].part_percent) or (
                    (summ[j].part_percent == summ[j + 1].part_percent) and (
                    summ[j].attendance_percent > summ[j + 1].attendance_percent)):
                temp = summ[j]
                summ[j] = summ[j + 1]
                summ[j + 1] = temp

    for i in range(len(summ)):
        summ[i].ranking = i + 1
    return render(request, 'rankings.html', {'page_title': 'User Rankings for ' + club_obj.name, 'summ_set': summ,
                                             'from_date': from_date,
                                             'to_date': to_date})


@login_required()
@request_passes_test(user_is_member)
def member_detail(request, club_id, member_id):
        # Roles Performed Count
        parts = Participation.objects.filter(member_id=member_id)
        member = Member.objects.get(id=member_id)
        part_summary = member.get_part_summary()
        return render(request, 'memberdetail.html', {'part_summary': part_summary, 'parts': parts} )


@login_required()
@request_passes_test(user_is_member)
def club_management(request, club_id):
    club_obj = Club.objects.get(pk=club_id)
    club_members = club_obj.members.filter(active=True)
    return render(request, 'manageclub.html', { 'club_members' : club_members})


@login_required()
@request_passes_test(user_is_ec)
def send_participation_email(request, club_id):
    try:
        t = threading.Thread(target=email_send_thread, args=(club_id,))
        t.daemon=True
        t.start()
    except:
        pass
    messages.info(request, 'Email will be sent to the members in background.')
    return redirect(request.META.get('HTTP_REFERER'))


def email_send_thread(club_id):
    club = Club.objects.get(id=club_id)
    club_mems = Member.objects.filter(club_id=club_id, active=True)
    part_types = Participation_Type.objects.all()
    tt = part_types.get(name='Table Topic')
    speech = part_types.get(name='Prepared Speech')
    evaluation = part_types.get(name='Evaluation')
    big_three = part_types.filter(category='Role-Advanced')
    mem_list = [mem.id for mem in club_mems]
    participation_count = Participation.get_participation_count(mem_list)
    part_percent_dict = {}
    for part_count in participation_count:
        part_percent_dict[part_count.id] = [part_count.TotalParticipations]
        part_percent_dict[part_count.id].append(
            math.ceil((part_count.TotalParticipations / part_count.TotalAttendance) * 100) \
                if part_count.TotalAttendance != 0 else 0)
    for mem in club_mems:

        meets_attended = Attendance.objects.filter(member_id=mem.id, present=True).count()
        meets_total = Attendance.objects.filter(member_id=mem.id).count()
        att_percent = math.ceil((meets_attended / meets_total) * 100) if meets_total != 0 else 0
        tt_count = Participation.objects.filter(participation_type=tt, member=mem).count()
        tt_percent = math.ceil((tt_count / meets_attended) * 100) if meets_attended != 0 else 0
        speech_count = Participation.objects.filter(participation_type=speech, member=mem).count()
        evaluation_count = Participation.objects.filter(participation_type=evaluation, member=mem).count()
        big_three_count = Participation.objects.filter(participation_type__in=big_three, member=mem).count()
        part_count = part_percent_dict[mem.id][0]
        part_percent = part_percent_dict[mem.id][1]
        html_template = loader.get_template('email/participation_summary.html')
        html_message = html_template.render({
            'meets_attended': meets_attended,
            'meets_total': meets_total,
            'att_percent': att_percent,
            'tt_count': tt_count,
            'tt_percent': tt_percent,
            'speech_count': speech_count,
            'evaluation_count': evaluation_count,
            'big_three_count': big_three_count,
            'part_count': part_count,
            'part_percent': part_percent,
            'club': club.name,
            'member_name': str(mem.user.full_name)
        })
        try:
            send_mail('Participation Summary of %s' % mem.user.full_name,
                      'Participation Summary of %s' % mem.user.full_name, 'smarttm@toastmasters.pk', [mem.user.email],
                      fail_silently=True, html_message=html_message)

            mem.summary_sent_date = timezone.now()
            mem.save()
        except:
            continue