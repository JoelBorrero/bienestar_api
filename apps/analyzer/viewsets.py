from rest_framework import viewsets

from .models import UploadedReport
from .serializers import UploadedReportSerializer


class UploadedReportViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedReportSerializer
    queryset = UploadedReport.objects.filter(deleted=False)
