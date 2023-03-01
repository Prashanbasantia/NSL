from django.urls import path
from ServiceApp import views
urlpatterns = [
    path('logout', views.logoutView, name="service_engineer_logout"),
    path('dashboard', views.dashboardView, name="service_engineer_dashboard"),
]
