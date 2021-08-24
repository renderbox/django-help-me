from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _ 


class CategoryChoices(models.IntegerChoices):
    COMMENT = 1, _("Comment")
    SALES = 2, _("Sales")
    HELP = 3, _("Help")
    BUG = 4, _("Bug")
    CONTACT = 5, _("Contact")

    
class AppSettings(object):

    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, default):
        return getattr(settings, self.prefix + name, default)

    @property
    def TICKET_CATEGORIES(self):
        """ Category choices for a support request ticket """
        return self._setting('TICKET_CATEGORIES', CategoryChoices)


app_settings = AppSettings('HELPME_')
