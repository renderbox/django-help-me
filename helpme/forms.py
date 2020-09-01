from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext as _

from helpme.models import Comment, Category, Question


class CommentForm(ModelForm):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'placeholder': 'Leave a comment'}))
    
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
        fields = ['category', 'sites']


class QuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = ['question', 'answer', 'category', 'sites']
