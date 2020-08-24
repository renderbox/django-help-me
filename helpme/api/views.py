from rest_framework.generics import CreateAPIView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from helpme.models import Ticket, Comment
from helpme.api.serializers import CommentSerializer


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
