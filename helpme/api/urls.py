from django.urls import path

from helpme.api import views

app_name = "helpme-api"

urlpatterns = [
    path('<uuid:uuid>/comment/', views.CreateCommentAPIView.as_view(), name='create-comment'),
]
