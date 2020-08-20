from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext as _

from helpme.models import Ticket, Comment


class SupportRequestForm(ModelForm):

    class Meta:
        model = Ticket
        fields = ['subject', 'description']


class CommentForm(ModelForm):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'placeholder': 'Leave a comment'}))
    
    class Meta:
        model = Comment
        fields = ['content', 'visibility']

    def __init__(self, support=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not support:
            self.fields.pop('visibility')
            
