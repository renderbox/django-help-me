from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext as _
from django.contrib.sites.models import Site

from helpme.models import Ticket, Comment, Category, Question, VisibilityChoices


class TicketForm(ModelForm):

    class Meta:
        model = Ticket
        fields = ['category', 'subject', 'description']


class CommentForm(ModelForm):
    content = forms.CharField(label=_("Message"), widget=forms.Textarea(attrs={'placeholder': 'Enter a message', 'rows': '4'}))
    visibility = forms.ChoiceField(label=_("Visibility (Who can see this message)"), choices=VisibilityChoices.choices)
    
    class Meta:
        model = Comment
        fields = ['content', 'visibility']

    def __init__(self, support=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not support:
            self.fields.pop('visibility')
            

class CategoryForm(ModelForm):

    class Meta:
        model = Category
        fields = ['category', 'sites', 'global_category', 'excluded_sites']

    def __init__(self, staff, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not staff:
            self.fields.pop('sites')
            self.fields.pop('global_category')
            self.fields.pop('excluded_sites')


class QuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = ['question', 'answer', 'category', 'sites', 'global_question', 'excluded_sites']

    def __init__(self, staff, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not staff:
            self.fields.pop('sites')
            self.fields.pop('global_question')
            self.fields.pop('excluded_sites')

            # limit the possible categories to the current site
            current_site = Site.objects.get_current()
            self.fields['category'].queryset = Category.objects.filter(sites__in=[current_site])
