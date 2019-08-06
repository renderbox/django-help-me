from django.views.generic import TemplateView

class HelpMeIndexView(TemplateView):
    template_name = "helpme/index.html"
