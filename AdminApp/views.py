from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout as log_out
# Create your views here.
from MainApp.models import CustomUsers, Employee, ServiceEngr
from django.db.models import Q
from django.db import transaction


def logoutView(request):
    log_out(request)
    return HttpResponseRedirect(reverse("login"))


def dashboardView(request):
    return render(request, 'AdminApp/dashboard.html')

# complaints View CRUD


def ComplaintCRView(request):  # sourcery skip: last-if-guard
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
            if not CustomUsers.objects.filter(Q(email=email) | Q(phone=email)).exists():
                messages.error(request, "Email of phone not found!")
                return HttpResponseRedirect(reverse('login'))

            if user is None:
                messages.error(request, "Invalid Password")
                return HttpResponseRedirect(reverse('login'))
            if not user.is_active:
                messages.error(
                    request, "Your account is disabled! please contact Admin.")
                return HttpResponseRedirect(reverse('login'))

        except Exception as e:
            messages.error(request, f"Server Error: {e}")
            return HttpResponseRedirect(reverse('login'))
    else:
        return render(request, 'MainApp/login.html')


# Employee View CRUD
def EmployeeCRView(request):  # sourcery skip: last-if-guard
    if request.method == "POST":
        try:
            name = request.POST.get("name", None)
            phone = request.POST.get("phone", None)
            email = request.POST.get("email", None)
            empid = request.POST.get("empid", None)
            designation = request.POST.get("designation", None)
            department = request.POST.get("department", None)
            print("POST", request.POST)
            if not email:
                messages.error(request, "Required email")
                return HttpResponseRedirect(reverse('admin_manage_employee'))
            if not phone:
                messages.error(request, "Required phone")
                return HttpResponseRedirect(reverse('admin_manage_employee'))
            if not name:
                messages.error(request, "Required name")
                return HttpResponseRedirect(reverse('admin_manage_employee'))
            if not empid:
                messages.error(request, "Required employee id")
                return HttpResponseRedirect(reverse('admin_manage_employee'))
            if not designation:
                messages.error(request, "Required designation")
                return HttpResponseRedirect(reverse('admin_manage_employee'))
            if not department:
                messages.error(request, "Required department")
                return HttpResponseRedirect(reverse('admin_manage_employee'))
            if CustomUsers.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return HttpResponseRedirect(reverse('admin_manage_employee'))
            if CustomUsers.objects.filter(phone=phone).exists():
                messages.error(request, "Phone already exists")
                return HttpResponseRedirect(reverse('admin_manage_employee'))
            password = f'{email.split("@")[0]}@{phone}'
            print("password", password)
            with transaction.atomic():
                user = CustomUsers.objects.create_user(
                    name=name, email=email, phone=phone, password=password, user_type="Employee")
                user.employee.empid = empid
                user.employee.designation = designation
                user.employee.department = department
                user.save()
                messages.success(request, "Employee created successfully")
                return HttpResponseRedirect(reverse('admin_manage_employee'))
        except Exception as e:
            messages.error(request, f"Server Error: {e}")
            return HttpResponseRedirect(reverse('admin_manage_employee'))
    else:
        employees = Employee.objects.select_related(
            'cu').all().order_by('-created_at')
        context = {
            "employees": employees
        }
        return render(request, 'AdminApp/manage_employee.html', context)


# Service Enginerr View CRUD
def ServiceEngineerCRView(request):  # sourcery skip: last-if-guard
    if request.method == "POST":
        try:
            name = request.POST.get("name", None)
            phone = request.POST.get("phone", None)
            email = request.POST.get("email", None)
            empid = request.POST.get("empid", None)
            designation = request.POST.get("designation", None)
            if not email:
                messages.error(request, "Required email")
                return HttpResponseRedirect(reverse('admin_manage_service_engineer'))
            if not phone:
                messages.error(request, "Required phone")
                return HttpResponseRedirect(reverse('admin_manage_service_engineer'))
            if not name:
                messages.error(request, "Required name")
                return HttpResponseRedirect(reverse('admin_manage_service_engineer'))
            if not empid:
                messages.error(request, "Required employee id")
                return HttpResponseRedirect(reverse('admin_manage_service_engineer'))
            if not designation:
                messages.error(request, "Required designation")
                return HttpResponseRedirect(reverse('admin_manage_service_engineer'))
            if CustomUsers.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return HttpResponseRedirect(reverse('admin_manage_service_engineer'))
            if CustomUsers.objects.filter(phone=phone).exists():
                messages.error(request, "Phone already exists")
                return HttpResponseRedirect(reverse('admin_manage_service_engineer'))
            password = f'{email.split("@")[0]}@{phone}'
            print("password", password)
            with transaction.atomic():
                user = CustomUsers.objects.create_user(
                    name=name, email=email, phone=phone, password=password, user_type="Service_Engineer")
                user.serviceengr.empid = empid
                user.serviceengr.designation = designation
                user.save()
                messages.success(
                    request, "Service Engineer created successfully")
                return HttpResponseRedirect(reverse('admin_manage_service_engineer'))
        except Exception as e:
            messages.error(request, f"Server Error: {e}")
            return HttpResponseRedirect(reverse('admin_manage_service_engineer'))
    else:
        service_engineers = ServiceEngr.objects.select_related(
            'cu').all().order_by('-created_at')
        context = {
            "service_engineers": service_engineers
        }
        return render(request, 'AdminApp/manage_service_engineer.html', context)
