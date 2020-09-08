from django import template

register = template.Library()

@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)

# find the ticket's last comment visible to the current user
@register.filter
def last_visible(ticket_comments, comments):
    last_visible = None
    for comment in ticket_comments.order_by('-created'):
        if comment in comments:
            last_visible = comment
            break
    return last_visible

@register.simple_tag
def url_replace(request, field, value):

    dict_ = request.GET.copy()

    dict_[field] = value

    return dict_.urlencode()

@register.simple_tag
def multiply(a, b):
    return a * b

