import uuid 
import datetime

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db import models


##################
# CHOICES
##################

# TODO: update categories
class CategoryChoices(models.IntegerChoices):
    COMMENT = 1, _("Comment")
    SALES = 2, _("Sales")
    HELP = 3, _("Help")
    BUG = 4, _("Bug")

class StatusChoices(models.IntegerChoices):
    OPEN = 1, _("Open")
    ACTIVE = 10, _("Active")
    HOLD = 20, _("Hold")
    CLOSED = 30, _("Closed")
    CANCELED = 40, _("Canceled")

class PriorityChoices(models.IntegerChoices):
    SUGGESTION = 1, _("Suggestion")
    LOW = 2, _("Low")
    MEDIUM = 3, _("Medium")
    HIGH = 4, _("High")
    URGENT = 5, _("Urgent")

class VisibilityChoices(models.IntegerChoices):
    REPORTERS = 1, _("Reporters")
    SUPPORT = 10, _("Support Handlers")
    DEVELOPERS = 15, _("Developers")
    SUPERVISORS = 20, _("Supervisors")


##################
# ABSTRACT MODELS
##################

class CreateUpdateModelBase(models.Model):
    created = models.DateTimeField("date created", auto_now_add=True)
    updated = models.DateTimeField("last updated", auto_now=True)

    class Meta:
        abstract = True

    def been_updated(self):
        return (self.updated - self.created) > datetime.timedelta(seconds=1)
    
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
    status = models.IntegerField(_("Status"), default=1, choices=StatusChoices.choices)
    priority = models.IntegerField(_("Priority"), default=3, choices=PriorityChoices.choices)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="support_tickets")
    user_meta = models.JSONField(blank=True, null=True, default=dict)
    category = models.IntegerField(_("Category"), default=3, choices=CategoryChoices.choices)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="support_tickets")
    subject = models.CharField(_("Subject"), max_length=120)
    description = models.TextField(_("Description"))
    history = models.JSONField(blank=True, null=True, default=list)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tickets")
    dev_ticket = models.CharField(max_length=30, blank=True, null=True)
    related_to = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return "{0} - {1}".format(self.user.username, self.subject)

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
    visibility = models.IntegerField(_("Visibility"), default=1, choices=VisibilityChoices.choices)

    def __str__(self):
        return "{0} - {1}".format(self.user.username, self.created)
