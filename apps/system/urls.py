from django.urls import path
# Create your views here.
from system.views.test import *
from rest_framework import routers

router = routers.SimpleRouter()

router.register(r'fakerdata', FakerDataViewSet, basename='fakerdata')
#router.register(r'test', MenuApiView, basename='test')
#urlpatterns = router.urls
urlpatterns = [
    #path("menu", GetMenu.as_view()),
    path('menu/', MenuApiView.as_view(), name='test'),
    path("createmenu/", CreateMenuOrPerm.as_view())
]
urlpatterns += router.urls