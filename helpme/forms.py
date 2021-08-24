from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model

from helpme.models import Ticket, Comment, Category, Question, Team, VisibilityChoices
from helpme.utils import get_current_site


class AnonymousTicketForm(ModelForm):
    full_name = forms.CharField(label=_("Full Name"), widget=forms.TextInput(attrs={"placeholder": _("Enter name")}))
    email = forms.EmailField(label=_("Email Address"), widget=forms.EmailInput(attrs={"placeholder": _("Enter email")}))
    phone_number = forms.CharField(label=_("Phone Number (Optional)"), required=False)
    
    class Meta:
        model = Ticket
        fields = ['full_name', 'email', 'phone_number', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].label = _("How Can We Help You?")
        self.fields['description'].widget.attrs.update({'placeholder': _('Enter Message'), 'rows': 4})

        
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
        self.fields['assigned_to'].label = _("Assigned to")
        self.fields['teams'].label = _("Teams")
        
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

    class Meta:
        model = Category
        fields = ['category']


class QuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = ['question', 'answer', 'category']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

        # limit the possible categories to the current site
        current_site = get_current_site(self.request)
        self.fields['category'].queryset = Category.objects.filter(category_sites__in=[current_site])
        self.fields['category'].label = _("Category")


class TeamForm(ModelForm):
    # get users with explicit support permissions
    # as well as admins with all permissions
    member_qs = get_user_model().objects.filter(user_permissions__codename="see_support_tickets") | get_user_model().objects.filter(is_superuser=True)
    members = forms.ModelMultipleChoiceField(queryset=member_qs.distinct(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Team
        fields = ['name', 'categories', 'members']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['members'].label = _("Members")


class SupportEmailForm(forms.Form):
    email = forms.EmailField(label=_("Support Email"), required=False)
