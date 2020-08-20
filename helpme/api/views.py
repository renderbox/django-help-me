#from rest_framework import generics
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from helpme.models import Ticket, Comment
from helpme.forms import CommentForm
# from helpme.api.serializers import SampleModelSerializer


# class SampleModelListAPIView(generics.ListAPIView):
#     queryset = SampleModel.objects.filter(enabled=True)
#     serializer_class = SampleModelSerializer

class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def get_success_url(self, *args, **kwargs):
        uuid = self.kwargs.get('ticket_uuid')
        return reverse_lazy('helpme:ticket-detail', args=[uuid])

    def form_valid(self, form, *args, **kwargs):
        uuid = self.kwargs.get('ticket_uuid')
        ticket = Ticket.objects.get(uuid=uuid)

        form.instance.user = self.request.user
        form.instance.ticket = ticket
        
        ticket.log_history_event(event="updated", user=self.request.user, notes="{0} left a comment".format(self.request.user.username))
        ticket.save()
        
        response = super().form_valid(form)
        return response


class UpdateCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def get_success_url(self, *args, **kwargs):
        uuid = self.kwargs.get('ticket_uuid')
        return reverse_lazy('helpme:ticket-detail', args=[uuid])

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        uuid = self.kwargs.get('comment_uuid')

        try:
            obj = queryset.get(uuid=uuid)
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def form_valid(self, form):
        uuid = self.kwargs.get('ticket_uuid')
        ticket = Ticket.objects.get(uuid=uuid)
        
        ticket.log_history_event(event="updated", user=self.request.user, notes="{0} updated their comment".format(self.request.user.username))
        ticket.save()
        
        response = super().form_valid(form)
        return response
