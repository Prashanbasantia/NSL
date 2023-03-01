from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render


class ProtectView(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user
        print(f'\n\n Module {modulename},  userType: {user} \n\n')
        if user.is_authenticated:
            if user.user_type == 'Admin':
                if modulename not in ['AdminApp.views', 'django.views.static']:
                    return HttpResponseRedirect(reverse("admin_dashboard"))
            elif user.user_type == 'Employee':
                if modulename not in ['EmployeeApp.views', 'django.views.static']:
                    return HttpResponseRedirect(reverse("employee_dashboard"))
            elif user.user_type == 'Service_Engineer':
                if modulename not in ['ServiceApp.views', 'django.views.static']:
                    return HttpResponseRedirect(reverse("service_engineer_dashboard"))
            else:
                return HttpResponseRedirect(reverse("login"))
        elif modulename not in ['MainApp.views', 'django.views.static']:
            return HttpResponseRedirect(reverse("login"))
