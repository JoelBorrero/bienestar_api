from django.urls import include, path
from rest_framework import routers

from .viewsets import PromoterViewSet, SupervisorViewSet

router = routers.DefaultRouter()
router.register(r"promoter", PromoterViewSet)
router.register(r"supervisor", SupervisorViewSet)

urlpatterns = [path("", include(router.urls))]
