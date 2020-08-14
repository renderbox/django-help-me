import uuid 

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField


DJANGO_PROJECT_VERSION = getattr(settings, "DJANGO_PROJECT_VERSION", None)

##################
# CHOICES
##################

# TODO: update categories
TICKET_CATEGORY_CHOICES = ( (1, _("Comment")), (2, _("Sales")), (3, _("Help")), (4, _("Bug")) )

TICKET_STATUS_CHOICES = ( (1, _("Open")), (10, _("Active")), (20, _("Hold")), (30, _("Closed")), (40, _("Canceled")) )

TICKET_PRIORITY_CHOICES = ( (1, _("Low")), (2, _("Medium")), (3, _("High")), (4, _("Urgent")) )

VISIBILITY_CHOICES = ( (1, _("Reporters")), (10, _("Support Handlers")), (15, _("Developers")), (20, _("Supervisors")) )


##################
# ABSTRACT MODELS
##################

class CreateUpdateModelBase(models.Model):
    created = models.DateTimeField("date created", auto_now_add=True)
    updated = models.DateTimeField("last updated", auto_now=True)

    class Meta:
        abstract = True


##################
# MODELS
##################

class Team(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=30)
    global_team = models.BooleanField()
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    

class Ticket(CreateUpdateModelBase):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.IntegerField(_("Status"), default=1, choices=TICKET_STATUS_CHOICES)
    priority = models.IntegerField(_("Priority"), default=2, choices=TICKET_PRIORITY_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="support_tickets")
    user_meta = JSONField(blank=True, null=True, default=dict)
    category = models.IntegerField(_("Category"), default=3, choices=TICKET_CATEGORY_CHOICES)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="support_tickets")
    subject = models.CharField(_("Subject"), max_length=120)
    description = models.TextField(_("Description"))
    history = JSONField(blank=True, null=True, default=list)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tickets")
    dev_ticket = models.CharField(max_length=30, blank=True, null=True)
    related_to = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return "{0}".format(self.subject)

    def log_history_event(self, event, user=None, notes=None, isotime=None):
        '''
        "history": [
            {
                "time": "2020-04-08T23:45:02.225609+00:00",
                "event": "created"
            }
        ],
        '''
        if not isotime:
            isotime = timezone.now().isoformat()           # '2019-12-18T22:27:28.222000+00:00'

        event = {'event':event, 'time':isotime}

        if user:
            event['user'] = user.pk
            event['username'] = user.username

        if notes:
            event['notes'] = notes

        self.history.append(event)

    
class Comment(CreateUpdateModelBase):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    content = models.TextField(_("Content"))
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    visibility = models.IntegerField(_("Visibility"), default=1, choices=VISIBILITY_CHOICES)
