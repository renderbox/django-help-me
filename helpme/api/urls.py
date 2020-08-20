from django.urls import path

from helpme.api import views

app_name = "helpme-api"

urlpatterns = [
    path('<str:ticket_uuid>/comment/', views.CreateCommentView.as_view(), name='create-comment'),
    path('<str:ticket_uuid>/comment/<str:comment_uuid>/', views.UpdateCommentView.as_view(), name='update-comment'),
]
