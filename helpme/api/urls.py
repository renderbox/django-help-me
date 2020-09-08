from django.urls import path

from helpme.api import views

urlpatterns = [
    path('ticket/', views.CreateTicketAPIView.as_view(), name='helpme-api-create-ticket'),
    path('<uuid:uuid>/comment/', views.CreateCommentAPIView.as_view(), name='helpme-api-create-comment'),
    path('category/', views.CreateCategoryAPIView.as_view(), name='helpme-api-create-category'),
    path('question/', views.CreateQuestionAPIView.as_view(), name='helpme-api-create-question'),
]
