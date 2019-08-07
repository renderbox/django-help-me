from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import SupportRequest
from .forms import SupportRequestForm, SupportRequestAnnonymousForm


class SupportRequestView(CreateView):
    model = SupportRequest
    success_url = reverse_lazy('helpme-success')
    category = 10

    def get_form_class(self):
        if self.request.user.is_authenticated:
            return SupportRequestForm
        return SupportRequestAnnonymousForm

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):

        if not form.instance.url:   # Fill it in with the page it is submitted from if it's not provided.
            form.instance.url = self.request.build_absolute_uri()

        form.instance.category = self.category

        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            form.instance.email = self.request.user.email
            form.instance.name = self.request.user.get_full_name()

        response = super().form_valid(form)

        if self.request.is_ajax():
            data = {
                'message': "Successfully submitted form data."
            }
            return JsonResponse(data)
        else:
            return response

            
class SupportRequestSuccessView(TemplateView):
    template_name = "helpme/submission_successful.html"
    
