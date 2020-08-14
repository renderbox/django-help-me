from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext as _

from helpme.models import Ticket


class SupportRequestForm(ModelForm):

    class Meta:
        model = Ticket
        fields = ['subject', 'description']
