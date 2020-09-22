from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext as _
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model

from helpme.models import Ticket, Comment, Category, Question, Team, VisibilityChoices


class TicketForm(ModelForm):

    class Meta:
        model = Ticket
        fields = ['category', 'subject', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].widget.attrs.update({'placeholder': _('Enter Subject Title')})
        self.fields['description'].widget.attrs.update({'placeholder': _('Enter Details')})


class UpdateTicketForm(ModelForm):
    teams = forms.ModelMultipleChoiceField(queryset=Team.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'category', 'teams', 'assigned_to', 'dev_ticket', 'question']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dev_ticket'].label = _("Developer Ticket")
        self.fields['question'].label = _("Related Frequently Asked Question")
        
        # filter teams by those that are responsible for the site where the ticket was created
        self.fields['teams'].queryset = Team.objects.filter(sites__in=[self.instance.site])


class CommentForm(ModelForm):
    content = forms.CharField(label=_("Message"), widget=forms.Textarea(attrs={'placeholder': _('Enter a message'), 'rows': '4'}))
    visibility = forms.ChoiceField(label=_("Visibility (Who can see this message)"), choices=VisibilityChoices.choices)
    
    class Meta:
        model = Comment
        fields = ['content', 'visibility']

    def __init__(self, support=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not support:
            self.fields.pop('visibility')
            

class CategoryForm(ModelForm):
    category_sites = forms.ModelMultipleChoiceField(queryset=Site.objects.all(), widget=forms.CheckboxSelectMultiple, label=_("Sites"))
    category_excluded_sites = forms.ModelMultipleChoiceField(queryset=Site.objects.all(), widget=forms.CheckboxSelectMultiple, label=_("Excluded sites"), required=False)
    
    class Meta:
        model = Category
        fields = ['category', 'global_category', 'category_sites', 'category_excluded_sites']

    def __init__(self, staff, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not staff:
            self.fields.pop('category_sites')
            self.fields.pop('global_category')
            self.fields.pop('category_excluded_sites')
        else:
            self.fields['global_category'].label = _("Global Category? (Appears on all sites except excluded sites)")


class QuestionForm(ModelForm):
    sites = forms.ModelMultipleChoiceField(queryset=Site.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    excluded_sites = forms.ModelMultipleChoiceField(queryset=Site.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = Question
        fields = ['question', 'answer', 'category', 'global_question', 'sites', 'excluded_sites']

    def __init__(self, staff, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not staff:
            self.fields.pop('sites')
            self.fields.pop('global_question')
            self.fields.pop('excluded_sites')

            # limit the possible categories to the current site
            current_site = Site.objects.get_current()
            self.fields['category'].queryset = Category.objects.filter(category_sites__in=[current_site])
        else:
            self.fields['global_question'].label = _("Global Question? (Appears on all sites except excluded sites)")


class TeamForm(ModelForm):
    # get users with explicit support permissions
    # as well as admins with all permissions
    member_qs = get_user_model().objects.filter(user_permissions__codename="see-support-tickets") | get_user_model().objects.filter(is_superuser=True)
    members = forms.ModelMultipleChoiceField(queryset=member_qs.distinct(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Team
        fields = ['name', 'categories', 'members']
