from rest_framework.generics import CreateAPIView

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from helpme.config import SupportEmailClass
from helpme.mixins import TicketMetaMixin
from helpme.models import Ticket, Comment, Category, Question, Team
from helpme.api.serializers import TicketSerializer, CommentSerializer, CategorySerializer, QuestionSerializer
from helpme.utils import get_current_site


class CreateTicketAPIView(LoginRequiredMixin, TicketMetaMixin, CreateAPIView):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()

    # make separate function so it can be overriden with a different template
    def send_email(self, serializer, instance, support_email):
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

    def perform_create(self, serializer):
        user_meta = self.get_ticket_request_meta(self.request)

        current_site = get_current_site(self.request)
        instance = serializer.save(user=self.request.user, site=current_site, user_meta=user_meta)

        # filter and assign teams by site and category
        teams = Team.objects.filter(sites__in=[instance.site])
        instance.teams.set(teams.filter(categories__contains=instance.category))

        config = SupportEmailClass(current_site)
        support_email = config.get_key_value().get("support_email")
        if support_email:
            self.send_email(serializer, instance, support_email)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if request.user.has_perm('helpme.see_support_tickets'):
            return redirect('helpme_admin:dashboard')
        return redirect('helpme:dashboard')
    

class CreateCommentAPIView(LoginRequiredMixin, CreateAPIView):
    lookup_field = 'uuid'
    serializer_class = CommentSerializer
    queryset = Ticket.objects.all()

    def perform_create(self, serializer):
        ticket = self.get_object()
        instance = serializer.save(user=self.request.user, ticket=ticket)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        uuid = self.kwargs.get("uuid")
        if request.user.has_perm('helpme.see_support_tickets'):
            return redirect('helpme_admin:ticket-detail', uuid=uuid)
        else:
            return redirect('helpme:dashboard')


class CreateCategoryAPIView(LoginRequiredMixin, CreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.global_category:
            instance.category_sites.set(Site.objects.exclude(id__in=instance.category_excluded_sites.all()))
        elif not instance.category_sites.exists():
            current_site = get_current_site(self.request)
            instance.category_sites.add(current_site)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return redirect('helpme_admin:faq-create')


class CreateQuestionAPIView(LoginRequiredMixin, CreateAPIView):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.global_question:
            instance.sites.set(Site.objects.exclude(id__in=instance.excluded_sites.all()))
        elif not instance.sites.exists():
            current_site = get_current_site(self.request)
            instance.sites.add(current_site)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return redirect('helpme_admin:faq-create')
