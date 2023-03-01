from django.urls import path
from MainApp import views
urlpatterns = [
    path('', views.indexView, name="index"),
    path('status', views.IssueStatusView, name="status"),
    path('login', views.loginView, name="login"),
    path('raised_issue', views.raised_issue, name="raised_issue"),
]
