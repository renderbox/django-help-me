from django.utils.translation import ugettext_lazy as _
from siteconfigs.config import SiteConfigBaseClass
from .forms import SupportEmailForm
from .utils import get_current_site

class SupportEmailClass(SiteConfigBaseClass):
    label = _("Support Email")
    form_class = SupportEmailForm
    
    def __init__(self, request):
        site = get_current_site(request)
        self.key = ".".join([__name__, __class__.__name__])
        super().__init__(site, self.key)
