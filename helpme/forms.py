from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext as _

from helpme.models import SupportRequest

class SupportRequestForm(ModelForm):

    class Meta:
        model = SupportRequest
        fields = ['subject', 'description']


    # def __init__(self, *args, **kwargs):
    #     super(ContactMessageForm, self).__init__(*args, **kwargs)

    #     self.fields['name'].widget.attrs.update({'placeholder' : 'Name*', 'aria-required':'true'})
    #     self.fields['email'].widget.attrs.update({'placeholder' : 'Email', 'aria-required':'true'})
    #     self.fields['subject'].widget.attrs.update({'placeholder' : 'Subject (Optinal)', 'aria-required':'true'})
    #     self.fields['message'].widget.attrs.update({'placeholder' : 'Message*', 'aria-required':'true'})


class SupportRequestAnnonymousForm(ModelForm):

    class Meta:
        model = SupportRequest
        fields = ['name', 'email', 'subject', 'description']

    def __init__(self, *args, **kwargs):
        super(SupportRequestAnnonymousForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True
    
    # def __init__(self, *args, **kwargs):
    #     super(ContactMessageForm, self).__init__(*args, **kwargs)

    #     self.fields['name'].widget.attrs.update({'placeholder' : 'Name*', 'aria-required':'true'})
    #     self.fields['email'].widget.attrs.update({'placeholder' : 'Email', 'aria-required':'true'})
    #     self.fields['subject'].widget.attrs.update({'placeholder' : 'Subject (Optinal)', 'aria-required':'true'})
    #     self.fields['message'].widget.attrs.update({'placeholder' : 'Message*', 'aria-required':'true'})
