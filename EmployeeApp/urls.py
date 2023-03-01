from django.urls import path
from EmployeeApp import views
urlpatterns = [
    path('logout', views.logoutView, name="employee_logout"),
    path('dashboard', views.dashboardView, name="employee_dashboard"),
]
