
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Ticket


class SupportRequestView(LoginRequiredMixin, CreateView):
    model = Ticket
    success_url = reverse_lazy('helpme-success')
    category = 3
    fields = ['subject', 'description']

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        form.instance.category = self.category
        form.instance.user = self.request.user
        
        form.instance.log_history_event(event="created", user=self.request.user)

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
    

# class SupportDashboard(LoginRequiredMixin, ListView):
#     model = SupportRequest

#     # If you are logged in you see only your tickets

#     # if you are staff, you see tickets assigned to you or unassigned

#     # if you are admin, you see all tickets
