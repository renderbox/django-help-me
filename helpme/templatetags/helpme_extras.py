from django import template
from datetime import datetime

from helpme.models import CommentTypeChoices 

register = template.Library()

@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)

# find the ticket's last message visible to the current user
@register.filter
def last_visible(ticket_comments, comments):
    last_visible = None
    for comment in ticket_comments.filter(comment_type=CommentTypeChoices.MESSAGE).order_by('-created'):
        if comment in comments:
            last_visible = comment
            break
    return last_visible

@register.filter
def convert_isotime(isotime):
    return datetime.strptime(isotime[:19], '%Y-%m-%dT%H:%M:%S')

@register.simple_tag
def url_replace(request, field, value):

    dict_ = request.GET.copy()

    dict_[field] = value

    return dict_.urlencode()

