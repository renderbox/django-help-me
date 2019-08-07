from django.urls import path

from helpme import views

urlpatterns = [
    path("", views.HelpMeIndexView.as_view(), name="helpme-index"),
    path("request/", views.SupportRequestView.as_view(), name="helpme-submit-request"),
    path("success/", views.SupportRequestSuccessView.as_view(), name="helpme-success"),
]
