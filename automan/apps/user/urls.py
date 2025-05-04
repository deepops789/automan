from django.urls import path
from . import views
from .views import *
from rest_framework import routers

router = routers.SimpleRouter()

urlpatterns = [
    path("auth/", UserAuthView.as_view()),
    path("info", UserInfoView.as_view()),
    path("perm", PermView.as_view()),
    path("codes", UserCodesView.as_view()),
    path("logout", LogoutView.as_view()),
]
