from django.shortcuts import render
from smarttm_web.models import Meeting, User, Member, Club, Participation, Summary, Participation_Type
from django.shortcuts import render_to_response
import pdb

# Create your views here.

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def meeting(request, meeting_id):
    return HttpResponse("This meeting was held on %s" % str(Meeting.objects.get(pk = meeting_id).meeting_date))

def summary(request, club_key):
    
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
    
    
    
    return render(request, 'rankings.html' , {'summ_set' : summ, 'FromDate': FromDate, 'ToDate':ToDate})