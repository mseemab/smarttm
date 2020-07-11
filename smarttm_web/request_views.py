from django.shortcuts import render
from smarttm_web.models import Requests, Club, Participation_Type, Member
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.db.models import Q
from django.urls import reverse
from smarttm_web.decorators import request_passes_test
from smarttm_web.request_tests import user_is_member, user_is_ec
import pdb


@login_required()
@request_passes_test(user_is_ec)
def requests_view(request, club_id):
    club_requests = Requests.objects.filter(club_id=club_id)
    member= Member.objects.get(club_id=club_id, user=request.user)
    return render(request, 'requests.html', {'reqs': club_requests,
                                                     'pending_count': Requests.objects.filter(club_id=club_id, status="Unassigned").count(),
                                                     'all_count': club_requests.count(),
                                                     'my_count': Requests.objects.filter(member=member).count()
                                                     })

@login_required()
@request_passes_test(user_is_ec)
def pending_requests_view(request, club_id):
    unassigned_requests = Requests.objects.filter(club_id=club_id, status="Unassigned")
    member= Member.objects.get(club_id=club_id, user=request.user)
    return render(request, 'requests.html', {'reqs': unassigned_requests,
                                                     'pending_count': unassigned_requests.count(),
                                                     'all_count': Requests.objects.filter(club_id=club_id).count(),
                                                     'my_count': Requests.objects.filter(member=member).count()
                                                     })


@login_required()
@request_passes_test(user_is_member)
def my_requests_view(request, club_id):
    member = Member.objects.get(club_id=club_id, user=request.user)
    user_requests = Requests.objects.filter(club_id=club_id, member=member)
    return render(request, 'requests.html', {'reqs': user_requests,
                                                     'pending_count': Requests.objects.filter(club_id=club_id, status="Unassigned").count(),
                                                     'all_count': Requests.objects.filter(club_id=club_id).count(),
                                                     'my_count': user_requests.count()
                                                     })


def requests_new(request, club_id):
    if request.method == 'POST':
        part_type_id = request.POST.get('part_type_id')
        request_date = request.POST.get('request_date')
        member = Member.objects.get(club_id=club_id, user=request.user)
        req_new = Requests.objects.create(participation_type_id=part_type_id,
                                            requested_date=request_date,
                                            club_id=club_id,
                                            member=member,
                                            status='Unassigned')
        req_new.save()
        return redirect('club_requests',club_id=club_id)
    part_types = Participation_Type.objects.all()
    return render(request, 'request_new.html', {'part_types': part_types})