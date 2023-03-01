from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout as log_out
# Create your views here.
from django.db.models import Q
from django.db import transaction
from MainApp.models import Issues


def logoutView(request):
    log_out(request)
    return HttpResponseRedirect(reverse("login"))


def dashboardView(request):
    return render(request, 'AdminApp/dashboard.html')


def manageIssuesView(request):
    issues = Issues.objects.all().order_by('-created_at')
    return render(request, 'AdminApp/manage_issues.html', {'issues': issues})

# complaints View CRUD
