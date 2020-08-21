from django.urls import path

from helpme.api import views

app_name = "helpme-api"

urlpatterns = [
    path('<uuid:uuid>/comment/', views.CreateUpdateCommentAPIView.as_view(), name='create-comment'),
    path('<uuid:ticket_uuid>/comment/<uuid:uuid>/', views.CreateUpdateCommentAPIView.as_view(), name='update-comment'),
]
