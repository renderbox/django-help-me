from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site

from helpme.models import Ticket, Comment, Team, Question, Category, VisibilityChoices, StatusChoices
from helpme.forms import TicketForm, CommentForm


class FAQView(LoginRequiredMixin, TemplateView):
    template_name = "helpme/faq.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = Site.objects.get_current()
        categories = Category.objects.filter(category_sites__in=[current_site])
        context['categories'] = categories
        if not categories.exists():
            context['questions'] = Question.objects.filter(sites__in=[current_site])
        return context


class SupportRequestView(LoginRequiredMixin, CreateView):
    model = Ticket
    success_url = reverse_lazy('helpme:dashboard')
    form_class = TicketForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.site = Site.objects.get_current()

        user_agent = self.request.user_agent

        if user_agent.is_mobile:
            device = "mobile"
        elif user_agent.is_pc:
            device = "pc"
        elif user_agent.is_tablet:
            device = "tablet"
        else:
            device = "unknown"

        form.instance.user_meta = {
            "browser": {
                "family": user_agent.browser.family,
                "version": user_agent.browser.version_string
            },
            "os": {
                "family": user_agent.os.family,
                "version": user_agent.os.version_string
            },
            "device": user_agent.device.family,
            "mobile_tablet_or_pc": device,
            "ip_address": self.request.META['REMOTE_ADDR']
        }

        response = super().form_valid(form)

        # filter and assign teams by site and category
        teams = Team.objects.filter(sites__in=[form.instance.site])
        form.instance.teams.set(teams.filter(categories__contains=form.instance.category))

        return response


class SupportDashboardView(LoginRequiredMixin, ListView):
    model = Ticket
    paginate_by = 10

    def get_paginate_by(self, queryset):
        if 'paginate_by' in self.request.GET:
            # returning the value doesn't work, have to explicitly set it
            self.paginate_by = int(self.request.GET['paginate_by']) # force to int just in case there's mischief

        return self.paginate_by

    def get_queryset(self, **kwargs):
        # admin
        if self.request.user.has_perm('helpme.see_all_tickets'):
            queryset = Ticket.objects.all()
        # support team member
        # sees tickets that are assigned to them or to a team they belong to
        # but are not assigned to a specific user yet
        elif self.request.user.has_perm('helpme.see_support_tickets'):
            tickets = Ticket.objects.filter(assigned_to=self.request.user) | Ticket.objects.filter(teams__in=self.request.user.team_set.all(), assigned_to=None)
            queryset = tickets.distinct()
        # platform user
        else:
            queryset = Ticket.objects.filter(user=self.request.user)

        # filter by status
        s = self.request.GET.get('s', '')
        if s:
            status = s.split(',')
            for stat in status:
                stat = int(stat)
            queryset = queryset.filter(status__in=status)
        else:
            # exclude closed tickets by default
            queryset = queryset.exclude(status=StatusChoices.CLOSED)
            
        return queryset.order_by('-priority')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        support = self.request.user.has_perm('helpme.see_support_tickets')
        developer = self.request.user.has_perm('helpme.see_developer_tickets')
        admin = self.request.user.has_perm('helpme.see_all_tickets')
        
        context['support'] = support
        context['statuses'] = StatusChoices.choices
        context['s'] = self.request.GET.get('s', '')
        context['pagination'] = self.paginate_by
        
        # determines whether status color is red or green
        context['negative_status'] = [StatusChoices.CLOSED, StatusChoices.CANCELED, StatusChoices.HOLD]
        
        context['ticket_form'] = TicketForm
        context['comment_form'] = CommentForm(support=support)

        # filter comments by visibility
        if admin:
            comments = Comment.objects.all()
        else:
            comments = Comment.objects.filter(visibility=VisibilityChoices.REPORTERS)
            if support:
                comments |=  Comment.objects.filter(visibility=VisibilityChoices.SUPPORT)
            if developer:
                comments |= Comment.objects.filter(visibility=VisibilityChoices.DEVELOPERS)
        context['comments'] = comments
        return context
    
