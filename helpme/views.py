
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.sites.models import Site

from .models import Ticket, Team
from .forms import CommentForm


class SupportRequestView(LoginRequiredMixin, CreateView):
    model = Ticket
    success_url = reverse_lazy('helpme:success')
    category = 3
    fields = ['subject', 'description', 'category']

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        form.instance.category = self.category
        form.instance.user = self.request.user
        form.instance.site = Site.objects.get_current()
        
        form.instance.log_history_event(event="created", user=self.request.user)

        response = super().form_valid(form)

        # filter and assign teams by site and category
        teams = Team.objects.filter(sites__in=[form.instance.site])
        form.instance.teams.set(teams.filter(categories__contains=self.category))
        form.instance.save()

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
        if self.request.user.has_perm('helpme.see-all-tickets'):
            queryset = Ticket.objects.all()
        # support team member
        # sees tickets that are assigned to them or to a team they belong to
        # but are not assigned to a specific user yet
        elif self.request.user.has_perm('helpme.see-support-tickets'):
            tickets = Ticket.objects.none()
            for team in self.request.user.team_set.all():
                tickets = tickets | Ticket.objects.filter(teams__in=[team])
            queryset = Ticket.objects.filter(assigned_to=self.request.user) | tickets.filter(assigned_to=None)
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
    fields = ['status', 'priority', 'category', 'teams', 'assigned_to', 'dev_ticket', 'related_to']
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
        support = self.request.user.has_perm('helpme.see-support-tickets')
        
        context['support'] = support
        context['developer'] = self.request.user.has_perm('helpme.see-developer-tickets')
        context['supervisor'] = self.request.user.has_perm('helpme.see-all-tickets')

        context['user'] = self.request.user
        context['comment_form'] = CommentForm(support=support)
        context['comments'] = self.object.comments.all()
        return context

    def form_valid(self, form):
        form.instance.log_history_event(event="updated", user=self.request.user)
        response = super().form_valid(form)
        return response


class TeamCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'helpme.view_team'
    model = Team
    fields = ['name', 'global_team', 'sites', 'categories', 'members']
    success_url = reverse_lazy('helpme:team-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = Team.objects.all()
        context['admin'] = self.request.user.has_perm('helpme.add_team')
        context['user_teams'] = self.request.user.team_set.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.global_team:
            form.instance.sites.set(Site.objects.all())
            form.instance.save()
        return response
    
class TeamDetailView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'helpme.view_team'
    model = Team
    fields = ['name', 'global_team', 'sites', 'categories', 'members']
    template_name = "helpme/team_detail.html"

    def get_success_url(self):
        return reverse_lazy('helpme:team-detail', args=[self.object.uuid])

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

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.global_team:
            form.instance.sites.set(Site.objects.all())
            form.instance.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin'] = self.request.user.has_perm('helpme.change_team')
        return context
