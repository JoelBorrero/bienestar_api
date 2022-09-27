from django.urls import include, path
from rest_framework import routers

from . import viewsets


router = routers.DefaultRouter()
router.register(r'reports', viewsets.UploadedReportViewSet)

urlpatterns = [
    path('', include(router.urls))
]
