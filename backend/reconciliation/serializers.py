from rest_framework import serializers


class DisagreementSerializer(serializers.Serializer):
    reason = serializers.CharField()
    record_id = serializers.CharField(allow_null=True)
    field = serializers.CharField(allow_null=True)
    system_a_value = serializers.JSONField(allow_null=True)
    system_b_value = serializers.JSONField(allow_null=True)
    system_a = serializers.JSONField(allow_null=True)
    system_b = serializers.JSONField(allow_null=True)
    location = serializers.CharField(
        allow_null=True
    )
    organization = serializers.CharField(
        allow_null=True
    )