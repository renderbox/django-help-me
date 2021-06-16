from django.urls import path

from helpme.views import helpme as views

app_name = "helpme"

urlpatterns = [
    path("contact/", views.AnonymousTicketView.as_view(), name="anonymous"),
    path("dashboard/", views.SupportDashboardView.as_view(), name="dashboard"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("request/", views.SupportRequestView.as_view(), name="submit-request"),
]
