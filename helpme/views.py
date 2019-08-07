from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .models import SupportRequest
from .forms import SupportRequestForm, SupportRequestAnnonymousForm


class HelpMeIndexView(TemplateView):
    template_name = "helpme/index.html"


class SupportRequestView(CreateView):
    model = SupportRequest
    success_url = reverse_lazy('helpme-success')

    def get_form_class(self):
        if self.request.user.is_authenticated:
            return SupportRequestForm
        return SupportRequestAnnonymousForm


class SupportRequestSuccessView(TemplateView):
    template_name = "helpme/submission_successful.html"
    