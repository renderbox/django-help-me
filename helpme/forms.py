from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext as _

from helpme.models import SupportRequest

class SupportRequestForm(ModelForm):

    class Meta:
        model = SupportRequest
        fields = ['subject', 'description', 'url']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['url'].widget = forms.HiddenInput()


class SupportRequestAnnonymousForm(ModelForm):

    class Meta:
        model = SupportRequest
        fields = ['name', 'email', 'subject', 'description', 'url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['url'].widget = forms.HiddenInput()
