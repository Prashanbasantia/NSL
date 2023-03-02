from django.db import models
from django.utils.translation import gettext_lazy as _
from .utils import getId, generate_ticket_no


ISSUE_TYPE_CHOICES = [
    ('Printer', "PRINTER"),
    ('Network', "NETWORK"),
    ('Computer', "COMPUTER"),
    ('Software', "SOFTWARE"),
    ('Other', "OTHER")
]

COMPLAINT_STATUS_CHOICES = [
    ('Unassigned', "UNASSIGNED"),
    ('Assigned', "ASSIGNED"),
    ('Rejected', "REJECTED"),
    ('Completed', "COMPLETED")
]


class Issues(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    issue_type = models.CharField(
        default=ISSUE_TYPE_CHOICES[0][0], choices=ISSUE_TYPE_CHOICES, max_length=15)
    status = models.CharField(
        default=COMPLAINT_STATUS_CHOICES[0][0], choices=COMPLAINT_STATUS_CHOICES, max_length=15)
    ticket_no = models.CharField(max_length=50)
    emp_email = models.EmailField(_('email address'))
    emp_name = models.CharField(max_length=50)
    emp_phone = models.CharField(max_length=10)
    emp_designation = models.CharField(max_length=50)
    emp_department = models.CharField(max_length=50)
    emp_empid = models.CharField(max_length=20)
    description = models.TextField()
    location = models.CharField(max_length=259)
    assign_name = models.CharField(max_length=50, null=True)
    assign_phone = models.CharField(max_length=10, null=True)
    issue_date = models.DateTimeField()
    resolved_date = models.DateTimeField(null=True)
    rejected_date = models.DateTimeField(null=True)
    rejected_reason = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('user')
            while Issues.objects.filter(id=self.id).exists():
                self.id = getId('issue')
        if not self.ticket_no:
            total = Issues.objects.all().count()
            if total > 0:
                new_total = total + 1
                self.ticket_no = generate_ticket_no(str(new_total), 'NSLT')
                while Issues.objects.filter(ticket_no=self.ticket_no).exists():
                    new_total += 1
                    self.ticket_no = generate_ticket_no(str(new_total), 'NSLT')
            else:
                self.ticket_no = generate_ticket_no(None, 'NSLT')
        super(Issues, self).save()
