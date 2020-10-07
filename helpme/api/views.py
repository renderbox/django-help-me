from rest_framework.generics import CreateAPIView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.shortcuts import redirect

from helpme.models import Ticket, Comment, Category, Question, Team
from helpme.api.serializers import TicketSerializer, CommentSerializer, CategorySerializer, QuestionSerializer


class CreateTicketAPIView(LoginRequiredMixin, CreateAPIView):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()

    def perform_create(self, serializer):
        user_agent = self.request.user_agent
        
        if user_agent.is_mobile:
            device = "mobile"
        elif user_agent.is_pc:
            device = "pc"
        elif user_agent.is_tablet:
            device = "tablet"
        else:
            device = "unknown"

        user_meta = {
            "browser": {
                "family": str.lower(user_agent.browser.family),
                "version": user_agent.browser.version_string
            },
            "os": {
                "family": str.lower(user_agent.os.family),
                "version": user_agent.os.version_string
            },
            "device": str.lower(user_agent.device.family),
            "mobile_tablet_or_pc": device,
            "ip_address": self.request.META['REMOTE_ADDR']
        }
        
        instance = serializer.save(user=self.request.user, site=Site.objects.get_current(), user_meta=user_meta)

        # filter and assign teams by site and category
        teams = Team.objects.filter(sites__in=[instance.site])
        instance.teams.set(teams.filter(categories__contains=instance.category))

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
            instance.category_sites.add(Site.objects.get_current())

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
            instance.sites.add(Site.objects.get_current())

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return redirect('helpme_admin:faq-create')
