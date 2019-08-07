from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .models import SupportRequest
from .forms import SupportRequestForm, SupportRequestAnnonymousForm

class HelpMeIndexView(CreateView):
    # template_name = "helpme/index.html"
    model = SupportRequest
    # form_class = SupportRequestForm

    def get_form_class(self):
        if self.request.user.is_authenticated:
            return SupportRequestForm
        return SupportRequestAnnonymousForm