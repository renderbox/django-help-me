from django.urls import path

from helpme import views

# Paths for managing support requests go here...
urlpatterns = [
    # path("", views.HelpMeDashboardView.as_view(), name="helpme-dashboard"),
    path("request/", views.SupportRequestView.as_view(), name="helpme-submit-request"),
    path("success/", views.SupportRequestSuccessView.as_view(), name="helpme-success"),
]

