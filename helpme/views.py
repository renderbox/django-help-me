from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.sites.models import Site

from .models import Ticket, Comment, Team, Question, Category, VisibilityChoices, StatusChoices, CommentTypeChoices
from .forms import TicketForm, UpdateTicketForm, CommentForm, QuestionForm, CategoryForm, TeamForm


class FAQView(LoginRequiredMixin, TemplateView):
    template_name = "helpme/faq.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = Site.objects.get_current()
        categories = Category.objects.filter(category_sites__in=[current_site])
        context['categories'] = categories
        if not categories.exists():
            context['questions'] = Question.objects.filter(sites__in=[current_site])
        context['admin'] = self.request.user.has_perm('helpme.see-all-tickets')
        is_staff = self.request.user.is_staff
        context['question_form'] = QuestionForm(staff=is_staff)
        context['category_form'] = CategoryForm(staff=is_staff)
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
            device = "Mobile",
        elif user_agent.is_pc:
            device = "PC"
        elif user_agent.is_tablet:
            device = "Tablet"
        else:
            device = "Unknown"

        form.instance.user_meta = {
            "Browser": user_agent.browser.family + " " + user_agent.browser.version_string,
            "Operating System": user_agent.os.family + " " + user_agent.os.version_string,
            "Device": user_agent.device.family,
            "Mobile/Tablet/PC": device,
            "IP Address": self.request.META['REMOTE_ADDR']
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
        if self.request.user.has_perm('helpme.see-all-tickets'):
            queryset = Ticket.objects.all()
        # support team member
        # sees tickets that are assigned to them or to a team they belong to
        # but are not assigned to a specific user yet
        elif self.request.user.has_perm('helpme.see-support-tickets'):
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
        support = self.request.user.has_perm('helpme.see-support-tickets')
        developer = self.request.user.has_perm('helpme.see-developer-tickets')
        admin = self.request.user.has_perm('helpme.see-all-tickets')
        
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
    

class TicketDetailView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Ticket
    form_class = UpdateTicketForm
    template_name = "helpme/ticket_detail.html"
    permission_required = "helpme.see-support-tickets"

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

    def sort_comments(self):
        ticket = self.get_object()
        if 'oldest' in self.request.GET:
            return ticket.comments.all().order_by('created')
        else:
            return ticket.comments.all().order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        support = self.request.user.has_perm('helpme.see-support-tickets')
        developer = self.request.user.has_perm('helpme.see-developer-tickets')
        admin = self.request.user.has_perm('helpme.see-all-tickets')
        
        context['support'] = support
        context['developer'] = developer
        context['admin'] = admin

        context['user'] = self.request.user
        context['comment_form'] = CommentForm(support=support)
        context['ticket_form'] = TicketForm
        
        # determines whether status color is red or green
        context['negative_status'] = [StatusChoices.CLOSED, StatusChoices.CANCELED, StatusChoices.HOLD]

        # filter comments by visibility
        if admin:
            comments = self.object.comments.all()
        else:
            comments = self.object.comments.filter(visibility=VisibilityChoices.REPORTERS)
            if support:
                comments |=  self.object.comments.filter(visibility=VisibilityChoices.SUPPORT)
            if developer:
                comments |= self.object.comments.filter(visibility=VisibilityChoices.DEVELOPERS)
        context['comments'] = comments
        context['ticket_comments'] = self.sort_comments
        return context

    def form_valid(self, form):
        action = " updated the "
        cd = form.changed_data
        length = len(cd)
        for field in cd:
            if length > 1:
                if field == cd[-1]:
                    action += "and " + field + " fields"
                else:
                    if length == 2:
                        action += field + " "
                    else:
                        action += field + ", "
            else:
                action += field + " field"    
        Comment.objects.create(content=action, user=self.request.user, ticket=self.get_object(), comment_type=CommentTypeChoices.EVENT, visibility=VisibilityChoices.SUPPORT)
        
        response = super().form_valid(form)
        return response


class TeamCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'helpme.view_team'
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy('helpme:team-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin'] = self.request.user.has_perm('helpme.add_team')
        context['user_teams'] = self.request.user.team_set.all()
        context['teams'] = Team.objects.filter(sites__in=[Site.objects.get_current()])
        return context
    

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.sites.add(Site.objects.get_current())
        return response
    
    
class TeamDetailView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'helpme.view_team'
    model = Team
    form_class = TeamForm
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


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin'] = self.request.user.has_perm('helpme.change_team')
        return context
