from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from helpme.config import SupportEmailClass
from helpme.models import Ticket, Comment, Team, VisibilityChoices, StatusChoices, CommentTypeChoices
from helpme.forms import TicketForm, UpdateTicketForm, CommentForm, QuestionForm, CategoryForm, TeamForm, SupportEmailForm
from helpme.utils import get_current_site
from .helpme import FAQView, SupportDashboardView


class FAQCreateView(PermissionRequiredMixin, FAQView):
    template_name = "helpme/faq_create.html"
    permission_required = ["helpme.view_question", "helpme.view_category"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_form'] = QuestionForm(request=self.request)
        context['category_form'] = CategoryForm
        return context
    

class AdminSupportDashboardView(PermissionRequiredMixin, SupportDashboardView):
    permission_required = "helpme.see_support_tickets"
    template_name = "helpme/admin_ticket_list.html"


class SupportEmailView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = "helpme.see_all_tickets"
    template_name = "helpme/support_email.html"
    form_class = SupportEmailForm
    success_url = reverse_lazy("helpme_admin:support-email")

    def form_valid(self, form):
        result = super().form_valid(form)
        site = get_current_site(self.request)
        SupportEmailClass(site).save(form.cleaned_data["email"], "support_email")
        return result

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        config = SupportEmailClass(get_current_site(self.request))
        support_email = config.get_key_value().get("support_email")
        form = config.form_class(initial={"email": support_email})
        context["form"] = form
        return context
    

class TicketDetailView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Ticket
    form_class = UpdateTicketForm
    template_name = "helpme/ticket_detail.html"
    permission_required = "helpme.see_support_tickets"

    def get_success_url(self):
        return reverse_lazy('helpme_admin:ticket-detail', args=[self.object.uuid])
    
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
        support = self.request.user.has_perm('helpme.see_support_tickets')
        developer = self.request.user.has_perm('helpme.see_developer_tickets')
        admin = self.request.user.has_perm('helpme.see_all_tickets')
        
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
        context = {
            "changed_fields": form.changed_data,
            "user": self.request.user.username,
            "multiple": len(form.changed_data) > 1
        }
        action = render_to_string('helpme/event_comment.txt', context)
        Comment.objects.create(content=action, user=self.request.user, ticket=self.get_object(), comment_type=CommentTypeChoices.EVENT, visibility=VisibilityChoices.SUPPORT)
        
        response = super().form_valid(form)
        return response


class TeamCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'helpme.view_team'
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy('helpme_admin:team-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin'] = self.request.user.has_perm('helpme.add_team')
        context['user_teams'] = self.request.user.team_set.all()
        current_site = get_current_site(self.request)
        context['teams'] = Team.objects.filter(sites__in=[current_site])
        return context
    

    def form_valid(self, form):
        response = super().form_valid(form)
        current_site = get_current_site(self.request)
        form.instance.sites.add(current_site)
        return response
    
    
class TeamDetailView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'helpme.view_team'
    model = Team
    form_class = TeamForm
    template_name = "helpme/team_detail.html"

    def get_success_url(self):
        return reverse_lazy('helpme_admin:team-detail', args=[self.object.uuid])

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
