from django.urls import path
from AdminApp import views
urlpatterns = [
    path('logout', views.logoutView, name="admin_logout"),
    path('dashboard', views.dashboardView, name="dashboard"),
    path('manage_issues', views.manageIssuesView, name="manage_issues"),
    path('update_issue_status', views.updateIssueStatusView,
         name="update_issue_status"),
]
