from django.contrib.sites.models import Site


def get_current_site(request):
    if hasattr(request, 'site'):
        current_site = request.site
    else:
        current_site = Site.objects.get_current()
    return current_site
