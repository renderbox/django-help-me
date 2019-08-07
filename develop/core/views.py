from django.views.generic import TemplateView

from helpme.views import SupportRequestView


class CoreIndexView(TemplateView):
    template_name = "core/index.html"


class SupportRequestApiView(SupportRequestView):
    '''
    Broken into a seperate view for testing using a different template that loads the JS code.
    '''
    template_name = "core/supportrequest_api_form.html"
    