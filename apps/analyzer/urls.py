from django.urls import include, path
from rest_framework import routers

from .viewsets import (
    PromoterViewSet,
    StatisticsViewSet,
    SupervisorViewSet,
    UploadedReportViewSet,
)

router = routers.DefaultRouter()
router.register(r"promoter", PromoterViewSet)
router.register(r"statistics", StatisticsViewSet)
router.register(r"supervisor", SupervisorViewSet)
router.register(r"reports", UploadedReportViewSet)

urlpatterns = [path("", include(router.urls))]
