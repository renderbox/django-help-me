import uuid 

from django.conf import settings
from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth import get_user_model

DJANGO_PROJECT_VERSION = getattr(settings, "DJANGO_PROJECT_VERSION", None)

##################
# CHOICES
##################

SUPPORT_REQUEST_CATEGORY_CHOICES = ( (1, _("Comment")), (2, _("Sales")), (3, _("Help")), (4, _("Bug")) )

SUPPORT_REQUEST_STATUS_CHOICES = ( (1, _("Open")), (10, _("Active")), (20, _("Hold")), (30, _("Closed")), (40, _("Canceled")) )

SUPPORT_EVENT_VISIBILITY_CHOICES = ( (1, _("Reporters")), (10, _("Support Handlers")), (20, _("Supervisors")) )

SUPPORT_EVENT_CATEGORY_CHOICES = ( (1, _("Logged Event")), (10, _("Note")), (20, _("Reply")) )


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

class SupportRequest(CreateUpdateModelBase):
    subject = models.CharField(_("Subject"), max_length=120)
    description = models.TextField(_("Description"))
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.SET_NULL, related_name="support_request")   # It is possible to get a request from non-logged in users.
    assignees = models.ManyToManyField(get_user_model(), verbose_name=_("Asignees"), related_name="support_request_assignments", blank=True)
    name = models.CharField(_("Name"), max_length=50, blank=True)       # Required if user is unknown
    email = models.EmailField(_("Email"), max_length=254, blank=True)   # Required if user is unknown
    url = models.URLField(_("URL"), max_length=200, blank=True, help_text="Where the URL from which it was initiate from.")
    app_version = models.CharField(_("Project Version"), max_length=12, blank=True)
    category = models.IntegerField(_("Category"), default=10, choices=SUPPORT_REQUEST_CATEGORY_CHOICES)
    status = models.IntegerField(_("Status"), default=1, choices=SUPPORT_REQUEST_STATUS_CHOICES)

    class Meta:
        verbose_name = _( "Support Request")
        verbose_name_plural = _( "Support Requests")

    def __str__(self):
        return "{0} - {1}".format(self.email, self.subject)

    def save(self):
        if DJANGO_PROJECT_VERSION:
            self.app_version = DJANGO_PROJECT_VERSION
        return super().save()

#     def get_absolute_url(self):
#         return reverse( "support_request_detail", kwargs={"uuid": self.uuid})


class SupportEvent(CreateUpdateModelBase):
    request = models.ForeignKey(SupportRequest, verbose_name=_("Support Event"), on_delete=models.CASCADE, related_name="support_events")
    description = models.TextField(_("Description"))
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    visibility = models.IntegerField(_("Visibility"), default=1, choices=SUPPORT_EVENT_VISIBILITY_CHOICES)
    category = models.IntegerField(_("Category"), default=1, choices=SUPPORT_EVENT_CATEGORY_CHOICES)

#     class Meta:
#         verbose_name = _( "Support Request")
#         verbose_name_plural = _( "Support Requests")

#     def __str__(self):
#         return "{0} - {1}".format(self.request.email, self.request.subject)

# #     def get_absolute_url(self):
# #         return reverse( "samplemodel_detail", kwargs={"uuid": self.uuid})
