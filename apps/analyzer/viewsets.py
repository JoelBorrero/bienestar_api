from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Record, UploadedReport
from .serializers import PromoterRecordSerializer, RecordSerializer, SupervisorRecordSerializer, UploadedReportSerializer
from apps.utils.permissions import IsAccount, IsPromoter, IsSupervisor


def create_report(serializer_class, request):
    serializer = serializer_class(data=request.data, context={'user': request.user})
    data = dict()
    if serializer.is_valid(raise_exception=True):
        record, created = serializer.save()
        # data = serializer.create(record).data
    return serializer.is_valid(), created


class PromoterViewSet(viewsets.GenericViewSet):
    serializer_class = PromoterRecordSerializer
    queryset = Record.objects.filter(deleted=False)
    permission_classes = (IsAuthenticated, IsAccount, IsPromoter)

    @action(detail=False, methods=['GET'])
    def pending_reports(self, request):
        """Promoter reports that are waiting to sign."""
        pending = Record.objects.filter(promoter=request.user.account, wake_up_calls=None)
        data = RecordSerializer(pending, many=True)
        return Response({'data': data.data})

    @action(detail=False, methods=['POST'])
    def report(self, request):
        """Promoter reports his worked hour."""
        data, created = create_report(self.serializer_class, request)
        return Response({'data': data, 'created': created})


class SupervisorViewSet(viewsets.GenericViewSet):
    serializer_class = SupervisorRecordSerializer
    queryset = Record.objects.filter(deleted=False)
    permission_classes = (IsAuthenticated, IsAccount, IsSupervisor)

    @action(detail=False, methods=['GET'])
    def pending_reports(self, request):
        """Promoter reports that are waiting to sign."""
        pending = Record.objects.filter(supervisor=request.user.account, is_signed=False)
        data = RecordSerializer(pending, many=True)
        return Response({'data': data.data})

    @action(detail=False, methods=['POST'])
    def report(self, request):
        """Promoter reports his worked hour."""
        data, created = create_report(self.serializer_class, request)
        return Response({'data': data, 'created': created})


class UploadedReportViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedReportSerializer
    queryset = UploadedReport.objects.filter(deleted=False)
