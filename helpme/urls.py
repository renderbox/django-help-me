from django.urls import path

from helpme import views

app_name = "helpme"

urlpatterns = [
    path("", views.SupportDashboardView.as_view(), name="dashboard"),
    path("request/", views.SupportRequestView.as_view(), name="submit-request"),
    path("ticket/<uuid:uuid>/", views.TicketDetailView.as_view(), name="ticket-detail"),
    path("teams/", views.TeamCreateView.as_view(), name="team-list"),
    path("teams/<uuid:uuid>/", views.TeamDetailView.as_view(), name="team-detail"),
]
