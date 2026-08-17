from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import SentimentSerializer
from ml_model.Main import analyser
from .utils import calculate_statistics
from dashboard.utils import cleanup_old_analyses
from dashboard.models import AnalysisResult

class SentimentAPI(APIView):

    def post(self,request):
        serializer = SentimentSerializer(
            data=request.data
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        topic = serializer.validated_data["topic"]
        results = analyser(topic,settings.YOUTUBE_API_KEY)
        statistics = calculate_statistics(results)

        analysis = AnalysisResult.objects.create(
            topic=topic,
            results=results,
            statistics=statistics
        )

        cleanup_old_analyses()

        return Response({
            "id":analysis.id,
            "topic":topic,
            "statistics":statistics,
            "results":results
            })