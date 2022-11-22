from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UploadedReport
from .serializers import UploadedReportSerializer
from .tasks import load_statistics, common_words_activities_months, graph_data_pie_chart_type, graph_data_categories_month, graph_data_common_words_months
from apps.utils.serializers import EmptySerializer


class StatisticsViewSet(viewsets.GenericViewSet):
    serializer_class = EmptySerializer
    queryset = UploadedReport.objects.filter(deleted=False)  # Ignore
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["GET"])
    def coverage(self, request):
        """Returns statistics results."""
        data = request.query_params
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        data = load_statistics(start_date, end_date)
        return Response(data)

    @action(detail=False, methods=["GET"])
    def common_words(self, request):
        """Returns most common words in activities by month."""
        data = request.query_params
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        data = common_words_activities_months(start_date, end_date)
        return Response(data)


    @action(detail=False, methods=["GET"])
    def graph_data_pie_chart_type(self, _):
        """Returns pie chart data for activity type"""
        data = graph_data_pie_chart_type()
        return Response(data)

    @action(detail=False, methods=["GET"])
    def graph_data_categories_month(self, request):
        """Returns graph data for activity categories for a month"""
        data = request.query_params
        month = data.get("month")
        data = graph_data_categories_month(month)
        return Response(data)

    @action(detail=False, methods=["GET"])
    def graph_data_common_words_months(self, request):
        """Returns the most common words on activities for a month"""
        data = request.query_params
        amount = data.get("amount")
        data = graph_data_common_words_months(40, amount, **data)
        return Response(data)


class UploadedReportViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedReportSerializer
    queryset = UploadedReport.objects.filter(deleted=False)
