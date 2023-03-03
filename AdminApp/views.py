from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout as log_out
# Create your views here.
from django.db.models import Q, Count
from django.db import transaction
from datetime import datetime, timedelta
from MainApp.models import Issues
import json
from django.views.decorators.csrf import csrf_exempt


def logoutView(request):
    log_out(request)
    return HttpResponseRedirect(reverse("login"))


def dashboardView(request):
    today = datetime.now().date()
    issues = Issues.objects.aggregate(
        unassigned_issue=(Count('id', filter=Q(status="Unassigned"))),
        assigned_issue=(Count('id', filter=Q(status="Assigned"))),
        completed_issue=(Count('id', filter=Q(status="Completed"))),
        rejected_issue=(Count('id', filter=Q(status="Rejected"))),
        today_raised=(Count('id', filter=Q(
            status="Unassigned", issue_date__date=today))),
        today_resolved=(Count('id', filter=Q(
            status="Completed", resolved_date__date=today))),
        computer_issue=(Count('id', filter=Q(issue_type="Computer"))),
        email_issue=(Count('id', filter=Q(issue_type="Email"))),
        network_issue=(Count('id', filter=Q(issue_type="Network"))),
        printer_issue=(Count('id', filter=Q(issue_type="Printer"))),
        software_issue=(Count('id', filter=Q(issue_type="Software"))),
        other_issue=(Count('id', filter=Q(issue_type="Other"))),
    )
    return render(request, 'AdminApp/dashboard.html', issues)


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
                if issue.status == "Completed":
                    messages.error(
                        request, "Issue already completed! Service engineer can't be assign")
                    return HttpResponseRedirect(reverse('manage_issues'))
                if issue.status == "Rejected":
                    messages.error(
                        request, "Issue already rejected! Service engineer can't be assign")
                    return HttpResponseRedirect(reverse('manage_issues'))
                issue.assign_name = assign_name
                issue.assign_phone = assign_phone
                if issue.status == "Unassigned":
                    issue.status = "Assigned"
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


def issuesReportView(request):
    if from_date := request.GET.get('from_date', None):
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
    else:
        from_date = (datetime.now() - timedelta(days=7)).date()

    if to_date := request.GET.get('to_date', None):
        to_date = datetime.strptime(to_date, '%Y-%m-%d')
    else:
        to_date = datetime.now().date()

    issues = Issues.objects.filter(status="Completed", created_at__date__gte=from_date,
                                   created_at__date__lte=to_date, ).order_by('-created_at')
    return render(request, 'AdminApp/issues_report.html', {'issues': issues, "from_date": from_date, "to_date": to_date})


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
            if status not in ['Assigned', 'Completed', "Rejected"]:
                messages.error(
                    request, "Issue status Assigned, Completed, Rejected")
                return HttpResponseRedirect(reverse('manage_issues'))
            with transaction.atomic():
                issue = Issues.objects.get(id=issue_id)
                if issue.assign_name == issue.assign_phone == None:
                    messages.error(
                        request, "To update issue status first assign a servcie engineer.")
                    return HttpResponseRedirect(reverse('manage_issues'))
                if issue.status == status:
                    messages.error(
                        request, f"Issue has been already {status} !")
                    return HttpResponseRedirect(reverse('manage_issues'))

                if issue.status in ["Assigned", "Rejected"] and status == "Completed":
                    issue.status = "Completed"
                    issue.resolved_date = datetime.now()
                    issue.rejected_date = None
                    issue.rejected_reason = None

                elif issue.status in ["Assigned", "Completed"] and status == "Rejected":
                    if rejected_reason := request.POST.get("rejected_reason", None):
                        issue.status = "Rejected"
                        issue.rejected_date = datetime.now()
                        issue.rejected_reason = rejected_reason
                        issue.resolved_date = None
                    else:
                        messages.error(request, "Required rejected reason.")
                        return HttpResponseRedirect(reverse('manage_issues'))

                elif issue.status in ["Completed", "Rejected"] and status == "Assigned":
                    print("Reject", request.POST)
                    issue.status = "Assigned"
                    issue.resolved_date = None
                    issue.rejected_date = None
                    issue.rejected_reason = None
                issue.save()
                messages.success(request, "Issue status updated successfullly")
                return HttpResponseRedirect(reverse('manage_issues'))
        except Exception as e:
            messages.error(request, f"Server Error: {e}")
            return HttpResponseRedirect(reverse('manage_issues'))
    else:
        messages.error(request, "Invalid Request! Require Post Method")
        return HttpResponseRedirect(reverse('manage_issues'))


@csrf_exempt
def issueAnalyticsView(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': "required post method"})
    try:
        from_date = (datetime.now() - timedelta(days=6)).date()
        to_date = datetime.now().date()
        date_list = [from_date + timedelta(days=x)
                     for x in range((to_date-from_date).days + 1)]
        issue_graph = Issues.objects.filter(created_at__date__gte=from_date, created_at__date__lte=to_date).values('created_at__date').annotate(
            unassigned_issue=(Count('id', filter=Q(status="Unassigned"))),
            assigned_issue=(Count('id', filter=Q(status="Assigned"))),
            completed_issue=(Count('id', filter=Q(status="Completed"))),
            rejected_issue=(Count('id', filter=Q(status="Rejected"))),

            computer_issue=(Count('id', filter=Q(issue_type="Computer"))),
            email_issue=(Count('id', filter=Q(issue_type="Email"))),
            network_issue=(Count('id', filter=Q(issue_type="Network"))),
            printer_issue=(Count('id', filter=Q(issue_type="Printer"))),
            software_issue=(Count('id', filter=Q(issue_type="Software"))),
            other_issue=(Count('id', filter=Q(issue_type="Other"))),

        )
        labels, unassigned, assigned, completed, rejected, computer, email, network, printer, software, other = ([
        ] for _ in range(11))

        def finddata(date):
            isu = list(filter(None, [
                value if value['created_at__date'] == date else {} for value in issue_graph]))
            if isu:
                unassigned.append(isu[0]['unassigned_issue'])
                assigned.append(isu[0]['assigned_issue'])
                completed.append(isu[0]['completed_issue'])
                rejected.append(isu[0]['rejected_issue'])

                computer.append(isu[0]['computer_issue'])
                email.append(isu[0]['email_issue'])
                network.append(isu[0]['network_issue'])
                printer.append(isu[0]['printer_issue'])
                software.append(isu[0]['software_issue'])
                other.append(isu[0]['other_issue'])
            else:
                unassigned.append(0)
                assigned.append(0)
                completed.append(0)
                rejected.append(0)

                computer.append(0)
                email.append(0)
                network.append(0)
                printer.append(0)
                software.append(0)
                other.append(0)
            labels.append(date.strftime('%d-%b'))
            return None
        list(map(finddata, date_list))

        issues_status_series = [
            {'name': 'Unassigned', 'data': unassigned},
            {'name': 'Assigned', 'data': assigned},
            {'name': 'Completed', 'data': completed},
            {'name': 'Rejected', 'data': rejected}
        ]
        issues_type_series = [
            {'name': 'Computer', 'data': computer},
            {'name': 'Email', 'data': email},
            {'name': 'Network', 'data': network},
            {'name': 'Printer', 'data': printer},
            {'name': 'Software', 'data': software},
            {'name': 'Other', 'data': other}
        ]
        data = {'labels': labels,
                'issues_status_series': issues_status_series,
                'issues_type_series': issues_type_series
                }
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': e})


def changeNameView(request):  # sourcery skip: last-if-guard
    if request.method == "POST":
        try:
            first_name = request.POST.get("first_name", None)
            last_name = request.POST.get("last_name", None)
            if not first_name:
                messages.error(request, "Required first name")
                return HttpResponseRedirect(reverse('manage_issues'))
            if not last_name:
                messages.error(request, "Required last name")
                return HttpResponseRedirect(reverse('manage_issues'))

            with transaction.atomic():
                user = request.user
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                messages.success(request, "Name Changed successfullly")
                return HttpResponseRedirect(reverse('manage_issues'))
        except Exception as e:
            messages.error(request, f"Server Error: {e}")
            return HttpResponseRedirect(reverse('manage_issues'))
    else:
        messages.error(request, "Invalid Request! Require Post Method")
        return HttpResponseRedirect(reverse('manage_issues'))
