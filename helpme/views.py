
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Ticket


class SupportRequestView(LoginRequiredMixin, CreateView):
    model = Ticket
    success_url = reverse_lazy('helpme:success')
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

            
class SupportRequestSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "helpme/submission_successful.html"


class SupportDashboardView(LoginRequiredMixin, ListView):
    model = Ticket

    def get_queryset(self, **kwargs):
        # supervisor
        if self.request.user.has_perm('see-all-tickets'):
            queryset = Ticket.objects.all()
        # support team member
        elif self.request.user.has_perm('see-support-tickets'):
            queryset = Ticket.objects.filter(assigned_to=self.request.user) | Ticket.objects.filter(assigned_to=None)
        # platform user
        else:
            queryset = Ticket.objects.filter(user=self.request.user)
        return queryset.order_by('-priority')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['support'] = self.request.user.has_perm('see-support-tickets')
        return context
    

class TicketDetailView(LoginRequiredMixin, UpdateView):
    model = Ticket
    fields = ['status', 'priority', 'category', 'team', 'assigned_to', 'dev_ticket', 'related_to']
    template_name = "helpme/ticket_detail.html"

    def get_success_url(self):
        return reverse_lazy('helpme:ticket-detail', args=[self.object.uuid])
    
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        uuid = self.kwargs.get('uuid')

        try:
            obj = queryset.get(uuid=uuid)
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['support'] = self.request.user.has_perm('see-support-tickets')
        return context

    def form_valid(self, form):
        form.instance.log_history_event(event="updated", user=self.request.user)
        response = super().form_valid(form)
        return response
    
# class SupportDashboard(LoginRequiredMixin, ListView):
#     model = SupportRequest

#     # If you are logged in you see only your tickets

#     # if you are staff, you see tickets assigned to you or unassigned

#     # if you are admin, you see all tickets
