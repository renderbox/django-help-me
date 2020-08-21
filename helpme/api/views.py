from rest_framework.generics import CreateAPIView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from helpme.models import Ticket, Comment
from helpme.api.serializers import CommentSerializer


class CreateUpdateCommentAPIView(LoginRequiredMixin, CreateAPIView):
    lookup_field = 'uuid'
    serializer_class = CommentSerializer

    def get_queryset(self):
        ticket_uuid = self.kwargs.get('ticket_uuid')
        if ticket_uuid:
            return Comment.objects.all()
        else:
            return Ticket.objects.all()

    def perform_create(self, serializer):
        ticket_uuid = self.kwargs.get('ticket_uuid')
        obj = self.get_object()
        
        # if updating a comment
        if ticket_uuid:
            serializer = self.get_serializer(obj, data=self.request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        
            ticket = Ticket.objects.get(uuid=ticket_uuid)
        
            ticket.log_history_event(event="updated", user=self.request.user, notes="{0} updated their comment".format(self.request.user.username))
            ticket.save()
            
        # if creating a comment
        else:
            instance = serializer.save(user=self.request.user, ticket=obj)
        
            obj.log_history_event(event="updated", user=self.request.user, notes="{0} left a comment".format(self.request.user.username))
            obj.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        ticket_uuid = self.kwargs.get("ticket_uuid")
        if ticket_uuid:
            return redirect('helpme:ticket-detail', uuid=ticket_uuid)
        uuid = self.kwargs.get("uuid")
        return redirect('helpme:ticket-detail', uuid=uuid)
