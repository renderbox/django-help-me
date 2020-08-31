from django.urls import path

from helpme.api import views

urlpatterns = [
    path('<uuid:uuid>/comment/', views.CreateCommentAPIView.as_view(), name='helpme-api-create-comment'),
]
