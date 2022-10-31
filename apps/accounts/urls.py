from django.urls import include, path
from rest_framework import routers

from . import viewsets


router = routers.DefaultRouter()
router.register(r'users', viewsets.AccountAuthViewSet)
router.register(r'auth', viewsets.AccountRegisterViewSet)
router.register(r'activity', viewsets.ActivityViewSet)
router.register(r'group', viewsets.GroupViewSet)

urlpatterns = [
    path('', include(router.urls))
]
