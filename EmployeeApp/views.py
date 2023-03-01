from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout as log_out
# Create your views here.
from MainApp.models import CustomUsers
from django.db.models import Q


def logoutView(request):
    log_out(request)
    return HttpResponseRedirect(reverse("login"))


def dashboardView(request):
    return render(request, 'EmployeeApp/dashboard.html')
