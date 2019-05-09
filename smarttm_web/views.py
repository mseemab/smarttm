from django.shortcuts import render
from smarttm_web.models import Meeting, User, Member, Club, Participation, Summary, Participation_Type
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
import numpy as np
from django.contrib.auth.decorators import login_required
from smarttm_web.forms import UserForm
# Create your views here.


@login_required()
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


        
#
# Login User & create sessions.
#        
def login_user(request):
    
    if request.method == 'POST':
        username = request.POST.get("email")
        password = request.POST.get("password")
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                
                login(request, user)
                
                # create sessions.
                # Get user clubs
                
                user_clubs = user.member_user.all()
                if not len(user_clubs) == 0:
                    UserClubData = []
                    for user_club in user_clubs:
                        UserClubData.append([user_club.club.pk, user_club.club.name])

                    request.session['UserClubs'] = UserClubData

                    request.session['SelectedClub'] = UserClubData[0]

                request.session.modified = True
                
                return redirect('/smarttm_web/summary')
                
            else:
                messages.warning(request, 'Your account is not activated') 
                response = redirect('/accounts/login/')
                return response
        else:
           messages.warning(request, 'Invalid email/password.') 
           response = redirect('/accounts/login/')
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


def set_club(request, club_id):
    
    club_details = Club.objects.get(pk=club_id)
    request.session['SelectedClub'] = [club_details.pk,club_details.name]
    request.session.modified = True
   
    return redirect('/smarttm_web/summary')


@login_required()
def meeting(request, meeting_id):
    return HttpResponse("This meeting was held on %s" % str(Meeting.objects.get(pk = meeting_id).meeting_date))

@login_required()
def ImportMembers(request):
   
    if request.method == 'POST':
        myfile = request.FILES['importfile']
        
        try:
            df = pd.read_csv(myfile)
            df = df.fillna(0)
        except Exception as e:
            messages.warning(request, 'Sheet Club Members not found in import file.') 
            return redirect('ManageClub')


        temp_columns = ["Customer ID", "Name", "Company / In Care Of", "Addr L1", "Addr L2", "Addr L3", "Addr L4", "Addr L5", "Country", "Member has opted-out of Toastmasters WHQ marketing mail", "Email", "Secondary Email", "Member has opted-out of Toastmasters WHQ marketing emails", "Home Phone", "Mobile Phone", "Additional Phone", "Member has opted-out of Toastmasters WHQ marketing phone calls", "Paid Until", "Member of Club Since", "Original Join Date", "status (*)", "Current Position", "Future Position", "Pathways Enrolled"]
        req_cols = {"Customer ID":True, "Name":True, "Company / In Care Of":False, "Addr L1":True, "Addr L2":False, "Addr L3":False, "Addr L4":False, "Addr L5":False, "Country":True, "Member has opted-out of Toastmasters WHQ marketing mail":False, "Email":True, "Secondary Email":False, "Member has opted-out of Toastmasters WHQ marketing emails":False, "Home Phone":False, "Mobile Phone":False, "Additional Phone":False, "Member has opted-out of Toastmasters WHQ marketing phone calls":False, "Paid Until":True, "Member of Club Since":False, "Original Join Date":False, "status (*)":True, "Current Position":False, "Future Position":False, "Pathways Enrolled":False}
        
        header = df.columns.tolist()
        if header == temp_columns:
            for key, value in req_cols.items():
                if value:
                    if df[key].isnull().values.any():
                        messages.warning(request, key + " values contain empty cell(s)!")
                        return redirect('ManageClub')
                
            # Data is valid. 
            user_list = []
            member_list = []

            club_key = request.session['SelectedClub'][0]
            club_obj = Club.objects.get(pk=club_key)

            club_members = list(Member.objects.filter(club=club_obj, status = True))


            for index, row in df.iterrows():

                #check if user exists already
                user_obj, created = User.objects.update_or_create(
                    email = row['Email'],
                    defaults = {'full_name':row['Name'],
                                "address" : row['Addr L1'],
                                "country" : row['Country'],
                                "home_phone" : row['Home Phone'],
                                "mobile_phone" : row['Mobile Phone'],
                                "address" : row['Addr L1'] + ' ' + row['Addr L1'] + ' ' + row['Addr L5'],
                                #"paid_until" : row['Paid Until'],
                                "toastmaster_id" : row['Customer ID']
                            }

                )

                status = True if row['status (*)'] == 'paid' else False

                is_ec = False if row['Current Position'] is None or row['Current Position'] == 0 else True

                user_list.append(user_obj)
                member_obj, created = Member.objects.update_or_create(
                    club = club_obj, user = user_obj,
                    defaults={'status' : status,
                              'is_EC': is_ec}
                )

                member_list.append(member_obj)

            club_member_ids = [member.pk for member in club_members]
            new_member_ids = [member.pk for member in member_list]
            unpaid_member_ids = tuple(set(club_member_ids) - set(new_member_ids))
            Member.objects.filter(id__in = unpaid_member_ids).update(status = False, is_EC = False)

            messages.warning(request, 'Members imported.')

            return redirect('ManageClub')
            
        else:
            messages.warning(request, 'Input Sheet does not follow template guidelines.') 
            return redirect('ManageClub')
        
    return redirect('ManageClub')

@login_required()
def summary(request):
    
    if request.user.is_authenticated:
        club_key = request.session['SelectedClub'][0]
        club_obj = Club.objects.get(pk=club_key)
            
        club_members = club_obj.member_set.filter(active=True)
        
        FromDate = ""
        ToDate = ""
        if request.method == 'POST':
             
            FromDate = request.POST.get("StartDate", "")
            ToDate = request.POST.get("EndDate", "")
            
            partication_set = club_obj.participation_set.filter(created_date__range=(FromDate, ToDate))
        else:
            partication_set = club_obj.participation_set.filter()
            
        partication_types = Participation_Type.objects.all()
        category_adv = partication_types.filter(category = 'Role-Advanced')
        category_basic = partication_types.filter(category = 'Role-Basic')
        summ = []
        
        for club_mem in club_members:
            sum_obj = Summary()
            sum_obj.member = club_mem
            sum_obj.tt_count = partication_set.filter(member = club_mem, participation_type = partication_types.get(name='Table Topic')).count()
            sum_obj.speeches_count = partication_set.filter(member = club_mem, participation_type = partication_types.get(name='Prepared Speech')).count()
            sum_obj.evaluation_count =partication_set.filter(member = club_mem, participation_type = partication_types.get(name='Evaluation')).count()
            
            for part_type in category_adv:
                sum_obj.adv_role_count = sum_obj.adv_role_count+partication_set.filter(member = club_mem, participation_type = part_type).count()
            for part_type in category_basic:
                sum_obj.basic_role_count = sum_obj.basic_role_count+partication_set.filter(member = club_mem, participation_type = part_type).count()
            
            summ.append(sum_obj)
        
        
        return render(request, 'rankings.html' , { 'page_title':'User Rankings for '+ club_obj.name , 'summ_set' : summ, 'FromDate': FromDate, 'ToDate':ToDate})
    else:
        response = redirect('/accounts/login/')
        return response


@login_required()
def my_space(request):
    if request.user.is_authenticated:

        # Roles Performed Count

        Particiation_types = Participation_Type.objects.all()

        role_type = Particiation_types.filter(category__icontains = 'Role')

        memberships = list(Member.objects.filter(user = request.user))

        user_participations = Participation.objects.filter(member__in = memberships)

        roles_performed_count = user_participations.filter(member__in = memberships, participation_type__in = role_type).values('participation_type').distinct().count()




        return render(request, 'myspace.html', {'Roles_Performed': roles_performed_count})
    else:
        response = redirect('/accounts/login/')
        return response

@login_required()
def club_management(request):
    if request.user.is_authenticated:
        # Need to get club ID from session.
        club_key = request.session['SelectedClub'][0]
        club_obj = Club.objects.get(pk=club_key)
            
        club_members = club_obj.member_set.filter(active=True)
        
        return render(request, 'manageclub.html', { 'club_members' : club_members})

    else:
        response = redirect('/accounts/login/')
        return response
