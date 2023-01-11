from django.template.defaultfilters import date as _date
from rest_framework import serializers

from .models import Record, Zone
from apps.utils.choices import PROMOTER, SUPERVISOR


def create_record(validated_data: dict, extra_data: dict):
    validated_data["start_date"] = validated_data["start_date"].replace(
        second=0, microsecond=0
    )
    validated_data["end_date"] = validated_data["end_date"].replace(
        second=0, microsecond=0
    )
    validated_data.update(extra_data)
    record, created = Record.objects.update_or_create(
        start_date=validated_data.pop("start_date"),
        end_date=validated_data.pop("end_date"),
        promoter=validated_data.pop("promoter"),
        zone=validated_data.pop("zone"),
        defaults=validated_data,
    )
    return record, created


def validate_record(data: dict):
    start, end = data["start_date"], data["end_date"]
    if start > end or start.minute != 30 or end.minute != 30:
        raise serializers.ValidationError("Dates must be closed in 0 or 30 minutes.")
    supervisor = data.get("supervisor")
    promoter = data.get("promoter")
    if supervisor and supervisor.role != SUPERVISOR:
        raise serializers.ValidationError("Supervisor is not a supervisor")
    if promoter and promoter.role != PROMOTER:
        raise serializers.ValidationError("Promoter is not a promoter")
    if bool(supervisor) != bool(data.get("was_supervised")):
        raise serializers.ValidationError(
            "Selected supervisor and was_supervised field didn't match."
        )


class PromoterRecordSerializer(serializers.ModelSerializer):
    def validate(self, data):
        validate_record(data)
        return data

    def create(self, validated_data):
        extra_data = {"is_signed": False, "promoter": self.context["user"].account}
        record, created = create_record(validated_data, extra_data)
        return record, created

    class Meta:
        model = Record
        exclude = (
            "deleted",
            "is_signed",
            "promoter",
            "supervisor_notes",
            "supervisor_wake_up_calls",
            "updated_at",
        )
        extra_kwargs = {
            "people_called": {"required": True},
            "promoter_notes": {"required": True},
            "wake_up_calls": {"required": True},
        }


class RecordSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    zone = serializers.SlugRelatedField(slug_field="name", read_only=True)
    supervisor = serializers.SlugRelatedField(slug_field="first_name", read_only=True)

    def get_duration(self, obj):
        return (obj.end_date - obj.start_date).seconds // 3600

    def get_start_date(self, obj):
        return _date(obj.start_date, "D j M - f A")

    def get_end_date(self, obj):
        return _date(obj.end_date, "D j M - f A")

    class Meta:
        model = Record
        exclude = ("deleted", "updated_at")


class SupervisorRecordSerializer(serializers.ModelSerializer):
    def validate(self, data):
        validate_record(data)
        return data

    def create(self, validated_data):
        extra_data = {
            "is_signed": True,
            "supervisor": self.context["user"].account,
            "was_supervised": True,
        }
        record, created = create_record(validated_data, extra_data)
        return record, created

    class Meta:
        model = Record
        exclude = (
            "deleted",
            "is_signed",
            "people_called",
            "promoter_notes",
            "supervisor",
            "updated_at",
            "wake_up_calls",
            "was_supervised",
        )
        extra_kwargs = {
            "supervisor_notes": {"required": True},
            "supervisor_wake_up_calls": {"required": True},
        }


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ("id", "name")
