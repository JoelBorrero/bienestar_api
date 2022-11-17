from django.urls import include, path
from rest_framework import routers

from . import viewsets


router = routers.DefaultRouter()
router.register(r"auth", viewsets.AccountAuthViewSet)
router.register(r"activity", viewsets.ActivityViewSet)
router.register(r"group", viewsets.GroupViewSet)
router.register(r"", viewsets.UserViewSet)

urlpatterns = [path("", include(router.urls))]
