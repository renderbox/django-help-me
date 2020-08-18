from django.urls import path

from helpme import views

app_name = "helpme"

urlpatterns = [
    path("", views.SupportDashboardView.as_view(), name="dashboard"),
    path("request/", views.SupportRequestView.as_view(), name="submit-request"),
    path("success/", views.SupportRequestSuccessView.as_view(), name="success"),
    path("ticket/<str:uuid>/", views.TicketDetailView.as_view(), name="ticket-detail"),
    # Paths for managing support requests go here...
]
