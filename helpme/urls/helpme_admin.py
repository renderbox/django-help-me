from django.urls import path

from helpme.views import helpme_admin as views

app_name = "helpme_admin"

urlpatterns = [
    path("faq/create/", views.FAQCreateView.as_view(), name="faq-create"),
    path("tickets/", views.AdminSupportDashboardView.as_view(), name="dashboard"),
    path("ticket/<uuid:uuid>/", views.TicketDetailView.as_view(), name="ticket-detail"),
    path("teams/", views.TeamCreateView.as_view(), name="team-list"),
    path("teams/<uuid:uuid>/", views.TeamDetailView.as_view(), name="team-detail"),
    path("email/", views.SupportEmailView.as_view(), name="support-email"),
]
