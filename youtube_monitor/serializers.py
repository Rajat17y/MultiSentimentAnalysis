from rest_framework import serializers

class StartMonitorSerializer(serializers.Serializer):
    video_url = serializers.CharField(max_length=500)

class PollMonitorSerializer(serializers.Serializer):
    video_id = serializers.CharField(max_length=20)
    page_token = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )