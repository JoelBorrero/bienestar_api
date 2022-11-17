from django.urls import include, path
from rest_framework import routers

from .viewsets import RecordViewSet, ZoneViewSet

router = routers.DefaultRouter()
router.register(r"record", RecordViewSet)
router.register(r"zone", ZoneViewSet)

urlpatterns = [path("", include(router.urls))]
