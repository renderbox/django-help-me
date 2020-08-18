from django.urls import path

from helpme import views

urlpatterns = [
    path("", views.SupportDashboardView.as_view(), name="helpme-dashboard"),
    path("request/", views.SupportRequestView.as_view(), name="helpme-submit-request"),
    path("success/", views.SupportRequestSuccessView.as_view(), name="helpme-success"),
    path("ticket/<str:uuid>/", views.TicketDetailView.as_view(), name="helpme-ticket-detail"),
    # Paths for managing support requests go here...
]
