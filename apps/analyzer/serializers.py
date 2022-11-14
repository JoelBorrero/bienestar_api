from rest_framework import serializers

from .models import UploadedReport


class UploadedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedReport
        fields = ("pk", "result")
