from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.utils.permissions import IsPromoter, IsSupervisor
from apps.utils.choices import PROMOTER, SUPERVISOR
from .models import Record, Zone
from .serializers import (
    PromoterRecordSerializer,
    RecordSerializer,
    SupervisorRecordSerializer,
    ZoneSerializer,
)


def create_report(serializer_class, request):
    request.data["was_supervised"] = True
    serializer = serializer_class(data=request.data, context={"user": request.user})
    data = dict()
    if serializer.is_valid(raise_exception=True):
        record, created = serializer.save()
        data = serializer_class(record).data
    return data, created


class RecordViewSet(viewsets.GenericViewSet):
    serializer_class = RecordSerializer
    queryset = Record.objects.filter(deleted=False)
    permission_classes = (IsPromoter | IsSupervisor | IsAdminUser,)

    @staticmethod
    def create(request):
        """Promoter/supervisor reports his worked hour."""
        if request.user.account.role == PROMOTER:
            serializer_class = PromoterRecordSerializer
        elif request.user.account.role == SUPERVISOR:
            serializer_class = SupervisorRecordSerializer
        serializer = serializer_class(data=request.data, context={"user": request.user})
        data = dict()
        if serializer.is_valid(raise_exception=True):
            record, created = serializer.save()
            data = serializer_class(record).data
        return Response({"data": data, "created": created})

    @staticmethod
    def list(request, *args, **kwargs):
        """List all records."""
        if request.user.is_superuser:
            records = Record.objects.all()
        else:
            records = Record.objects.filter(
                Q(supervisor=request.user.account) | Q(promoter=request.user.account)
            )
        data = RecordSerializer(records, many=True)
        return Response({"data": data.data})

    @action(["GET"], False)
    def pending(self, request):
        """Promoter/supervisor reports that are waiting to sign."""
        if request.user.account.role == PROMOTER:
            pending = Record.objects.filter(
                promoter=request.user.account, wake_up_calls=None
            )
        elif request.user.account.role == SUPERVISOR:
            pending = Record.objects.filter(
                supervisor=request.user.account, is_signed=False
            )
        data = RecordSerializer(pending, many=True)
        return Response({"data": data.data})


class ZoneViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ZoneSerializer
    queryset = Zone.objects.all()
    permission_classes = (IsAuthenticated,)

    # @action(detail=False, methods=["GET"])
    # def zones(self, request):
    #     """Promoter reports that are waiting to sign."""
    #     zones = Zone.objects.all()
    #     data = RecordSerializer(zones, many=True)
    #     return Response({"data": data.data})
