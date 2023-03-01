from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .model_manager import CustomUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import getId
from datetime import timedelta

USER_TYPE_CHOICES = [
    ('Admin', "ADMIN"),
    ('Employee', "EMPLOYEE"),
    ('Service_Engineer', "SERVICE_ENGiNEER")
]
ISSUE_TYPE_CHOICES = [
    ('Printer', "PRINTER"),
    ('Network', "NETWORK"),
    ('Computer', "COMPUTER"),
    ('Software', "SOFTWARE"),
    ('Other', "OTHER")
]

COMPLAINT_STATUS_CHOICES = [
    ('New', "NEW"),
    ('Open', "OPEN"),
    ('Closed', "CLOSED")
]


class CustomUsers(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    user_permissions = models.ManyToManyField(
        to='auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='permissions'
    )
    user_type = models.CharField(
        default=USER_TYPE_CHOICES[0][0], choices=USER_TYPE_CHOICES, max_length=25)
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('auth')
            while CustomUsers.objects.filter(id=self.id).exists():
                self.id = getId('cu')
        super(CustomUsers, self).save()


class Admin(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    cu = models.OneToOneField(CustomUsers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('admin')
            while Admin.objects.filter(id=self.id).exists():
                self.id = getId('admin')
        super(Admin, self).save()


class Employee(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    cu = models.OneToOneField(CustomUsers, on_delete=models.CASCADE)
    designation = models.CharField(max_length=50, null=True)
    department = models.CharField(max_length=50, null=True)
    empid = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('user')
            while Employee.objects.filter(id=self.id).exists():
                self.id = getId('emp')
        super(Employee, self).save()


class ServiceEngr(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    cu = models.OneToOneField(CustomUsers, on_delete=models.CASCADE)
    designation = models.CharField(max_length=50, null=True)
    empid = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('user')
            while ServiceEngr.objects.filter(id=self.id).exists():
                self.id = getId('svengr')
        super(ServiceEngr, self).save()


@receiver(post_save, sender=CustomUsers)
def create_user_data(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == USER_TYPE_CHOICES[0][0]:
            Admin.objects.create(cu=instance)  # auth means AuthUser Instace
        elif instance.user_type == USER_TYPE_CHOICES[1][0]:
            Employee.objects.create(cu=instance)
        elif instance.user_type == USER_TYPE_CHOICES[2][0]:
            ServiceEngr.objects.create(cu=instance)


@receiver(post_save, sender=CustomUsers)
def save_user_data(sender, instance, **kwargs):
    if instance.user_type == USER_TYPE_CHOICES[0][0]:
        instance.admin.save()
    elif instance.user_type == USER_TYPE_CHOICES[1][0]:
        instance.employee.save()
    elif instance.user_type == USER_TYPE_CHOICES[2][0]:
        instance.serviceengr.save()

# OTHER MODELS


class Complaints(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    issue_type = models.CharField(
        default=ISSUE_TYPE_CHOICES[0][0], choices=ISSUE_TYPE_CHOICES, max_length=15)
    status = models.CharField(
        default=COMPLAINT_STATUS_CHOICES[0][0], choices=COMPLAINT_STATUS_CHOICES, max_length=15)
    raised_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True)
    assined_to = models.ForeignKey(
        ServiceEngr, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    location = models.CharField(max_length=259)
    issue_date = models.DateTimeField(null=True)
    resolved_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('user')
            while Complaints.objects.filter(id=self.id).exists():
                self.id = getId('complt')
        super(Complaints, self).save()
