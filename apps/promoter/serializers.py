from rest_framework import serializers

from .models import Record
from apps.utils.exceptions import (
    DateValidationError,
    PeopleValidationError,
    SupervisorValidationError,
)


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
        raise DateValidationError()
    if data.get("supervisor", True) == data.get("promoter"):
        raise PeopleValidationError()
    if bool(data.get("supervisor")) != bool(data.get("was_supervised")):
        raise SupervisorValidationError()


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
        exclude = ("is_signed", "promoter")
        extra_kwargs = {
            "people_called": {"required": True},
            "wake_up_calls": {"required": True},
        }


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        exclude = ("updated_at", "deleted")


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
            "was_supervised",
            "supervisor",
            "is_signed",
            "wake_up_calls",
            "people_called",
        )
        extra_kwargs = {"supervisor_wake_up_calls": {"required": True}}
