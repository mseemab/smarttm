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


# Create your views here.



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
    
def set_club(request, club_id):
    
    club_details = Club.objects.get(pk=club_id)
    request.session['SelectedClub'] = [club_details.pk,club_details.name]
    request.session.modified = True
   
    return redirect('/smarttm_web/summary')


            
def meeting(request, meeting_id):
    return HttpResponse("This meeting was held on %s" % str(Meeting.objects.get(pk = meeting_id).meeting_date))


def ImportMembers(request):
   
    if request.method == 'POST':
        myfile = request.FILES['importfile']
        
        try:
            df = pd.read_excel(myfile, sheet_name='Club Members')
        except Exception as e:
            messages.warning(request, 'Sheet Club Members not found in import file.') 
            return redirect('ManageClub')
        pdb.set_trace()
        temp_columns = ["Customer ID", "Name", "Company / In Care Of", "Addr L1", "Addr L2", "Addr L3", "Addr L4", "Addr L5", "Country", "Member has opted-out of Toastmasters WHQ marketing mail", "Email", "Secondary Email", "Member has opted-out of Toastmasters WHQ marketing emails", "Home Phone", "Mobile Phone", "Additional Phone", "Member has opted-out of Toastmasters WHQ marketing phone calls", "Paid Until", "Member of Club Since", "Original Join Date", "status (*)", "Current Position", "Future Position", "Pathways Enrolled"]
        req_cols = req_columns = {"Customer ID":True, "Name":True, "Company / In Care Of":False, "Addr L1":True, "Addr L2":False, "Addr L3":False, "Addr L4":False, "Addr L5":True, "Country":True, "Member has opted-out of Toastmasters WHQ marketing mail":False, "Email":True, "Secondary Email":False, "Member has opted-out of Toastmasters WHQ marketing emails":False, "Home Phone":False, "Mobile Phone":True, "Additional Phone":False, "Member has opted-out of Toastmasters WHQ marketing phone calls":False, "Paid Until":True, "Member of Club Since":True, "Original Join Date":True, "status (*)":True, "Current Position":True, "Future Position":False, "Pathways Enrolled":False}
        
        header = df.columns.tolist()
        if header == temp_columns:
            for key, value in req_cols.items():
                if value:
                    if df[key].isnull().values.any():
                        messages.warning(request, key + " values contain empty cell(s)!")
                        return redirect('ManageClub')
                
            # Data is valid. 
            messages.warning(request, "Data is valid. ")
            return redirect('ManageClub')
            
        else:
            messages.warning(request, 'Input Sheet does not follow template guidelines.') 
            return redirect('ManageClub')
        
    return redirect('ManageClub')


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
        
        
        return render(request, 'rankings.html' , { 'summ_set' : summ, 'FromDate': FromDate, 'ToDate':ToDate})
    else:
        response = redirect('/accounts/login/')
        return response
        
        
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
