from django.urls import path

from helpme import views

urlpatterns = [
    path("request/", views.SupportRequestView.as_view(), name="helpme-submit-request"),
    path("success/", views.SupportRequestSuccessView.as_view(), name="helpme-success"),
    # Paths for managing support requests go here...
]
