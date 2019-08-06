from django.urls import path

from helpme import views

urlpatterns = [
    path("", views.HelpMeIndexView.as_view(), name="helpme_index"),
]
