from django.urls import include, path
from rest_framework import routers

from .viewsets import StatisticsViewSet, UploadedReportViewSet

router = routers.DefaultRouter()
router.register(r"statistics", StatisticsViewSet)
router.register(r"reports", UploadedReportViewSet)

urlpatterns = [path("", include(router.urls))]
