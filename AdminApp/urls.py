from django.urls import path
from AdminApp import views
urlpatterns = [
    path('logout', views.logoutView, name="admin_logout"),
    path('dashboard', views.dashboardView, name="dashboard"),
    path('manage_tickets', views.manageIssuesView, name="manage_issues"),
    path('tickets_report', views.issuesReportView, name="issues_report"),
    path('update_issue_status', views.updateIssueStatusView, name="update_issue_status"),
    path('issue_analytics', views.issueAnalyticsView, name="issue_analytics"),
    path('change_name', views.changeNameView, name="change_name"),
]
