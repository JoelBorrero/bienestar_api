from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Record, Zone
from .serializers import (
    PromoterRecordSerializer,
    RecordSerializer,
    SupervisorRecordSerializer,
    ZoneSerializer,
)
from apps.utils.permissions import IsAccount, IsPromoter, IsSupervisor


def create_report(serializer_class, request):
    request.data["was_supervised"] = True
    serializer = serializer_class(data=request.data, context={"user": request.user})
    data = dict()
    if serializer.is_valid(raise_exception=True):
        record, created = serializer.save()
        data = serializer_class(record).data
    return data, created


class PromoterViewSet(viewsets.GenericViewSet):
    serializer_class = PromoterRecordSerializer
    queryset = Record.objects.filter(deleted=False)
    permission_classes = (IsAuthenticated, IsAccount, IsPromoter)

    @action(detail=False, methods=["GET"])
    def pending_reports(self, request):
        """Promoter reports that are waiting to sign."""
        pending = Record.objects.filter(
            promoter=request.user.account, wake_up_calls=None
        )
        data = RecordSerializer(pending, many=True)
        return Response({"data": data.data})

    @action(detail=False, methods=["POST"])
    def report(self, request):
        """Promoter reports his worked hour."""
        data, created = create_report(PromoterRecordSerializer, request)
        return Response({"data": data, "created": created})


class SupervisorViewSet(viewsets.GenericViewSet):
    serializer_class = SupervisorRecordSerializer
    queryset = Record.objects.filter(deleted=False)
    permission_classes = (IsAuthenticated, IsAccount, IsSupervisor)

    @action(detail=False, methods=["GET"])
    def pending_reports(self, request):
        """Promoter reports that are waiting to sign."""
        pending = Record.objects.filter(
            supervisor=request.user.account, is_signed=False
        )
        data = RecordSerializer(pending, many=True)
        return Response({"data": data.data})

    @action(detail=False, methods=["POST"])
    def report(self, request):
        """Promoter reports his worked hour."""
        data, created = create_report(SupervisorRecordSerializer, request)
        return Response({"data": data, "created": created})


class ZoneViewSet(viewsets.ModelViewSet):
    serializer_class = ZoneSerializer
    queryset = Zone.objects.all()
    permission_classes = (IsAuthenticated,)

    # @action(detail=False, methods=["GET"])
    # def zones(self, request):
    #     """Promoter reports that are waiting to sign."""
    #     zones = Zone.objects.all()
    #     data = RecordSerializer(zones, many=True)
    #     return Response({"data": data.data})
