import uuid 

from django.conf import settings
from django.utils.translation import ugettext as _
from django.db import models


# Probably should move this to AppConfig
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', None)

if AUTH_USER_MODEL == None:
    from django.contrib.auth.models import User
    AUTH_USER_MODEL = User

DJANGO_PROJECT_VERSION = getattr(settings, "DJANGO_PROJECT_VERSION", None)


##################
# CHOICES
##################

SUPPORT_REQUEST_CATEGORY_CHOICES = ( (1, _("Comment")), (2, _("Help")), (3, _("Bug")) )

SUPPORT_REQUEST_STATUS_CHOICES = ( (1, _("Open")), (10, _("Active")), (20, _("Closed")) )

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
    user = models.ForeignKey(AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL, related_name="user")   # It is possible to get a request from non-logged in users.
    assignees = models.ManyToManyField(AUTH_USER_MODEL, verbose_name=_("Asignees"), related_name="assignees", blank=True)
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


# class SupportEvent(CreateUpdateModelBase):
#     request = models.ForeignKey(SupportRequest, verbose_name=_("Support Event"), on_delete=models.CASCADE)
#     description = models.TextField(_("Description"))
#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     user = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
#     user_visible = models.BooleanField(_("User Visible"))
#     category = models.IntegerField(_("Category"), default=1, choices=SUPPORT_EVENT_CATEGORY_CHOICES)

#     class Meta:
#         verbose_name = _( "Support Request")
#         verbose_name_plural = _( "Support Requests")

#     def __str__(self):
#         return "{0} - {1}".format(self.request.email, self.request.subject)

# #     def get_absolute_url(self):
# #         return reverse( "samplemodel_detail", kwargs={"uuid": self.uuid})
