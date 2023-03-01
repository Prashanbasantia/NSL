from django.urls import path
from MainApp import views
urlpatterns = [
    path('', views.loginView, name="login"),
]
