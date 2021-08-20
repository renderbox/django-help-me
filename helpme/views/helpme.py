from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from helpme.config import SupportEmailClass
from helpme.mixins import TicketMetaMixin
from helpme.models import Ticket, Comment, Team, Question, Category, VisibilityChoices, StatusChoices
from helpme.forms import TicketForm, CommentForm, AnonymousTicketForm
from helpme.settings import app_settings
from helpme.utils import get_current_site


class FAQView(TemplateView):
    template_name = "helpme/faq.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        categories = Category.objects.filter(category_sites__in=[current_site])
        context['categories'] = categories
        if not categories.exists():
            context['questions'] = Question.objects.filter(sites__in=[current_site])
        return context


class AnonymousTicketView(TicketMetaMixin, CreateView):
    model = Ticket
    form_class = AnonymousTicketForm
    success_url = reverse_lazy("helpme:anonymous")
    template_name = "helpme/anonymous_ticket.html"

    # make separate function so it can be overriden with a different template
    def send_email(self, form, support_email):
        instance = form.instance
        user_meta = instance.user_meta
        context = {
            "full_name": user_meta["full_name"],
            "email": user_meta["email"],
            "phone_number": user_meta["phone_number"],
            "description": instance.description
        }
        send_mail(
            str(_("[{0} {1}] {2} Ticket from {3}".format(instance.site.name, instance.pk, instance.get_category_display(), user_meta["email"]))),
            render_to_string("helpme/email/anonymous_ticket.txt", context),
            settings.DEFAULT_FROM_EMAIL,
            [support_email]
        )

    def form_valid(self, form):
        user_meta = self.get_ticket_request_meta(self.request)
        user_meta["full_name"] = form.cleaned_data.get("full_name")
        user_meta["email"] = form.cleaned_data.get("email")
        user_meta["phone_number"] = form.cleaned_data.get("phone_number")
        form.instance.user_meta = user_meta

        form.instance.site = get_current_site(self.request)

        form.instance.category = app_settings.TICKET_CATEGORIES.CONTACT
        form.instance.subject = _("Contact Us")

        response = super().form_valid(form)

        # filter and assign teams by site and category
        teams = Team.objects.filter(sites__in=[form.instance.site])
        form.instance.teams.set(teams.filter(categories__contains=form.instance.category))

        config = SupportEmailClass(form.instance.site)
        support_email = config.get_key_value().get("support_email")
        if support_email:
            self.send_email(form, support_email)

        return response


class SupportRequestView(LoginRequiredMixin, TicketMetaMixin, CreateView):
    model = Ticket
    success_url = reverse_lazy('helpme:dashboard')
    form_class = TicketForm

    # make separate function so it can be overriden with a different template
    def send_email(self, form, support_email):
        instance = form.instance
        context = {
            "category": instance.get_category_display(),
            "subject": instance.subject,
            "description": instance.description
        }
        send_mail(
            str(_("[{0} {1}] {2} Ticket from {3}".format(instance.site.name, instance.pk, instance.get_category_display(), instance.user))),
            render_to_string("helpme/email/user_ticket.txt", context),
            settings.DEFAULT_FROM_EMAIL,
            [support_email]
        )

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.site = get_current_site(self.request)
        form.instance.user_meta = self.get_ticket_request_meta(self.request)

        response = super().form_valid(form)

        # filter and assign teams by site and category
        teams = Team.objects.filter(sites__in=[form.instance.site])
        form.instance.teams.set(teams.filter(categories__contains=form.instance.category))

        config = SupportEmailClass(form.instance.site)
        support_email = config.get_key_value().get("support_email")
        if support_email:
            self.send_email(form, support_email)

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
        site = get_current_site(self.request)
        # admin
        if self.request.user.is_staff or self.request.user.is_superuser:
            queryset = Ticket.objects.all()
        elif self.request.user.has_perm('helpme.see_all_tickets'):
            queryset = Ticket.objects.filter(site=site)
        # support team member
        # sees tickets that are assigned to them or to a team they belong to
        # but are not assigned to a specific user yet
        elif self.request.user.has_perm('helpme.see_support_tickets'):
            tickets = Ticket.objects.filter(site=site, assigned_to=self.request.user) | Ticket.objects.filter(site=site, teams__in=self.request.user.team_set.all(), assigned_to=None)
            queryset = tickets.distinct()
        # platform user
        else:
            queryset = Ticket.objects.filter(site=site, user=self.request.user)

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
            
        return queryset.order_by('-priority', '-updated')

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
    
