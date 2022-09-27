from rest_framework import serializers

from .models import UploadedReport


class UploadedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedReport
        fields = (
            'uuid',
            'result'
        )
        extra_kwargs = {
            'uuid': {
                'read_only': True
            }
        }
