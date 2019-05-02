from django.shortcuts import render
from smarttm_web.models import Meeting

# Create your views here.

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def meeting(request, meeting_id):
    return HttpResponse("This meeting was held on %s" % str(Meeting.objects.get(pk = meeting_id).meeting_date))