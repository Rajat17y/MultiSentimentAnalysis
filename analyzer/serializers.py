from rest_framework import serializers

class SentimentSerializer(serializers.Serializer):
    topic = serializers.CharField(
        required=True,
        allow_blank=False
    )