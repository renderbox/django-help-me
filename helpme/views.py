from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.conf import settings

from .models import SupportRequest
from .forms import SupportRequestForm, SupportRequestAnnonymousForm



class HelpMeIndexView(TemplateView):
    template_name = "helpme/index.html"


class SupportRequestView(CreateView):
    model = SupportRequest
    success_url = reverse_lazy('helpme-success')
    category = 10

    def get_form_class(self):
        if self.request.user.is_authenticated:
            return SupportRequestForm
        return SupportRequestAnnonymousForm

    def form_valid(self, form):
        form.instance.url = self.request.build_absolute_uri()
        form.instance.category = self.category

        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            form.instance.email = self.request.user.email
            form.instance.name = self.request.user.get_full_name()

        return super().form_valid(form)


class SupportRequestSuccessView(TemplateView):
    template_name = "helpme/submission_successful.html"
    