from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout as log_out
# Create your views here.
from django.db.models import Q, Count
from django.db import transaction
from datetime import datetime
from MainApp.models import Issues


def logoutView(request):
    log_out(request)
    return HttpResponseRedirect(reverse("login"))


def dashboardView(request):
    today = datetime.now().date()
    issues = Issues.objects.aggregate(
                new_issue=(Count('id', filter=Q(status="New"))),
                open_issue=(Count('id', filter=Q(status="Open"))),
                closed_issue=(Count('id', filter=Q(status="Closed"))),
                today_raised=(Count('id', filter=Q(status="New", issue_date__date = today))),
                today_resolved=(Count('id', filter=Q(status="Closed", resolved_date__date = today))),
                computer_issue=(Count('id', filter=Q(issue_type="Computer"))),
                network_issue=(Count('id', filter=Q(issue_type="Network"))),
                printer_issue=(Count('id', filter=Q(issue_type="Printer"))),
                software_issue=(Count('id', filter=Q(issue_type="Software"))),
                other_issue=(Count('id', filter=Q(issue_type="Other"))),
                )
    issues['total_issue'] = issues['new_issue'] + issues['open_issue'] + issues['closed_issue'] 
    return render(request, 'AdminApp/dashboard.html',issues)


def manageIssuesView(request):
    if request.method == "POST":
        try:
            issue_id = request.POST.get("issue_id", None)
            assign_name = request.POST.get("assign_name", None)
            assign_phone = request.POST.get("assign_phone", None)
            if not issue_id:
                messages.error(request, "Required issue id")
                return HttpResponseRedirect(reverse('manage_issues'))
            if not assign_name:
                messages.error(request, "Required service engineer name")
                return HttpResponseRedirect(reverse('manage_issues'))
            if not assign_phone:
                messages.error(request, "Required service engineer phone")
                return HttpResponseRedirect(reverse('manage_issues'))
            with transaction.atomic():
                issue = Issues.objects.get(id=issue_id)
                if issue.status == "Closed":
                    messages.error(
                        request, "Issue was closed! Service engineer can't be assign")
                    return HttpResponseRedirect(reverse('manage_issues'))
                issue.assign_name = assign_name
                issue.assign_phone = assign_phone
                if issue.status == "New":
                    issue.status = "Open"
                issue.save()
                messages.success(
                    request, "Service engineer assigned successfullly")
                return HttpResponseRedirect(reverse('manage_issues'))
        except Exception as e:
            messages.error(request, f"Server Error: {e}")
            return HttpResponseRedirect(reverse('manage_issues'))
    else:
        issues = Issues.objects.all().order_by('-created_at')
        return render(request, 'AdminApp/manage_issues.html', {'issues': issues})


def updateIssueStatusView(request):  # sourcery skip: last-if-guard
    if request.method == "POST":
        try:
            issue_id = request.POST.get("issue_id", None)
            status = request.POST.get("status", None)
            if not issue_id:
                messages.error(request, "Required issue id")
                return HttpResponseRedirect(reverse('manage_issues'))
            if not status:
                messages.error(request, "Required issue status")
                return HttpResponseRedirect(reverse('manage_issues'))
            if status not in ['Open', 'Closed']:
                messages.error(request, "Issue status either Open or Closed")
                return HttpResponseRedirect(reverse('manage_issues'))
            with transaction.atomic():
                issue = Issues.objects.get(id=issue_id)
                if issue.assign_name == issue.assign_phone == None:
                    messages.error(
                        request, "To update issue status first assign a servcie engineer.")
                    return HttpResponseRedirect(reverse('manage_issues'))
                if issue.status == status == "Closed":
                    messages.error(
                        request, "Issue was already closed! To reopen it set status Open")
                    return HttpResponseRedirect(reverse('manage_issues'))
                if issue.status == status == "Open":
                    messages.error(
                        request, "Issue was already Opened! To close it set status Closed")
                    return HttpResponseRedirect(reverse('manage_issues'))
                if issue.status == "Open" and status == "Closed":
                    issue.status = "Closed"
                    issue.resolved_date = datetime.now()
                if issue.status == "Closed" and status == "Open":
                    issue.status = "Open"
                    issue.resolved_date = None
                issue.save()
                messages.success(
                    request, "Issue status updated successfullly")
                return HttpResponseRedirect(reverse('manage_issues'))
        except Exception as e:
            messages.error(request, f"Server Error: {e}")
            return HttpResponseRedirect(reverse('manage_issues'))
    else:
        messages.error(request, "Invalid Request! Require Post Method")
        return HttpResponseRedirect(reverse('manage_issues'))
