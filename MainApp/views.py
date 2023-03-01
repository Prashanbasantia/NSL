from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login as log_in
# Create your views here.
from .models import CustomUsers
from django.db.models import Q
from .auth_backend import Login


def loginView(request):  # sourcery skip: last-if-guard
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
            user = Login.authenticate(request, email=email, password=password)
            if user is None:
                messages.error(request, "Invalid Password")
                return HttpResponseRedirect(reverse('login'))
            if not user.is_active:
                messages.error(
                    request, "Your account is disabled! please contact Admin.")
                return HttpResponseRedirect(reverse('login'))
            log_in(request, user)
            if user.user_type == "Admin":
                return HttpResponseRedirect(reverse('admin_dashboard'))
            elif user.user_type == "Employee":
                return HttpResponseRedirect(reverse("employee_dashboard"))
            elif user.user_type == "Service_Engineer":
                return HttpResponseRedirect(reverse("serviceengr_dashboard"))
            else:
                messages.error(
                    request, f"Unidentify user type: {user.user_type}")
                return HttpResponseRedirect(reverse('login'))
        except Exception as e:
            messages.error(request, f"Server Error: {e}")
            return HttpResponseRedirect(reverse('login'))
    else:
        return render(request, 'MainApp/login.html')
