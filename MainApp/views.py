from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login as log_in
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction
from MainApp.models import Issues
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from .utils import Syserror
UserModel = get_user_model()
ISSUE_TYPE_CHOICES = ['Printer', 'Network',
                      'Computer', 'Software', 'Email', 'Other']
ORG_CHOICES = ['NSL', 'Mecon' 'Other']


def indexView(request):  # sourcery skip: last-if-guard
    return render(request, 'MainApp/index.html')


@csrf_exempt
def raised_issue(request):
    if request.method != 'POST':
        resp_data = {"success": False, "message": "Required POST Method"}
        return JsonResponse(resp_data)
    try:
        data = json.loads(request.body)
        print("data", data)
        email = data.get("email", None)
        name = data.get("name", None)
        phone = data.get("phone", None)
        organization = data.get("organization", None)
        designation = data.get("designation", None)
        issue_type = data.get("issue_type", None)
        location = data.get("location", None)
        description = data.get("description", None)
        if not all([name, phone, organization, designation, issue_type, location, description]):
            resp_data = {"success": False, "message": "Required All Field"}
            return JsonResponse(resp_data)
        if organization not in ORG_CHOICES:
            resp_data = {"success": False, "message": "Invalid Organization"}

        if issue_type not in ISSUE_TYPE_CHOICES:
            resp_data = {"success": False, "message": "Invalid issue type"}
            return JsonResponse(resp_data)
        with transaction.atomic():
            issue = Issues.objects.create(
                emp_name=name, emp_email=email, emp_phone=phone, emp_organization=organization,
                emp_designation=designation, location=location, issue_type=issue_type,
                description=description, issue_date=datetime.now())
            resp_data = {"success": True, "message": "Issue raised successfully",
                         "ticket_number": issue.ticket_no}
            return JsonResponse(resp_data)

    except Exception as e:
        Syserror(e)
        resp_data = {"success": False, "message": f"{e}"}
        return JsonResponse(resp_data)


def IssueStatusView(request):  # sourcery skip: last-if-guard
    issue = None
    if ticket_number := request.GET.get("ticket_number", ''):
        if issueCheck := Issues.objects.filter(ticket_no=ticket_number):
            issue = issueCheck.first()
        else:
            messages.error(
                request, "Issue not found! Please enter a valid ticket no.")
    return render(request, 'MainApp/issue_status.html', {'issue': issue, 'ticket_number': ticket_number})


def loginView(request):  # sourcery skip: last-if-guard
    if request.method == "POST":
        try:
            email = request.POST.get("email", None)
            password = request.POST.get("password", None)
            if not email:
                messages.error(request, "Required email or phone")
                return HttpResponseRedirect(reverse('login'))
            if not password:
                messages.error(request, "Required Password")
                return HttpResponseRedirect(reverse('login'))
            if not UserModel.objects.filter(Q(email=email) | Q(username=email)).exists():
                messages.error(request, "Email of username not found!")
                return HttpResponseRedirect(reverse('login'))
            user = UserModel.objects.get(Q(email=email) | Q(username=email))
            if user.check_password(password):
                log_in(request, user)
                return HttpResponseRedirect(reverse('dashboard'))
            else:
                messages.error(request, "Invalid Password")
                return HttpResponseRedirect(reverse('login'))
        except Exception as e:
            messages.error(request, f"Server Error: {e}")
            return HttpResponseRedirect(reverse('login'))
    else:
        return render(request, 'MainApp/login.html')
