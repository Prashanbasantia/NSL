from django.urls import path
from AdminApp import views
urlpatterns = [
    path('logout', views.logoutView, name="admin_logout"),
    path('dashboard', views.dashboardView, name="admin_dashboard"),
    path('manage_employee', views.EmployeeCRView, name="admin_manage_employee"),
    path('manage_service_engineer', views.ServiceEngineerCRView,
         name="admin_manage_service_engineer"),
]
