from rest_framework.generics import CreateAPIView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.shortcuts import redirect

from helpme.models import Ticket, Comment, Category, Question
from helpme.api.serializers import CommentSerializer, CategorySerializer, QuestionSerializer


class CreateCommentAPIView(LoginRequiredMixin, CreateAPIView):
    lookup_field = 'uuid'
    serializer_class = CommentSerializer
    queryset = Ticket.objects.all()

    def perform_create(self, serializer):
        ticket = self.get_object()
        instance = serializer.save(user=self.request.user, ticket=ticket)
        
        ticket.log_history_event(event="updated", user=self.request.user, notes="{0} left a comment".format(self.request.user.username))
        ticket.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        uuid = self.kwargs.get("uuid")
        return redirect('helpme:ticket-detail', uuid=uuid)


class CreateCategoryAPIView(LoginRequiredMixin, CreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.global_category:
            instance.sites.set(Site.objects.exclude(id__in=instance.excluded_sites.all()))
        elif not instance.sites.exists():
            instance.sites.add(Site.objects.get_current())

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return redirect('helpme:faq')


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
        return redirect('helpme:faq')
