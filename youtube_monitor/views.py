from django.shortcuts import render
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    StartMonitorSerializer,
    PollMonitorSerializer
)

from .utils import (
    extract_video_id,
    fetch_video_info,
    get_live_chat_id,
    fetch_live_chat_messages,
    detect_spike
)

from ml_model.ModelImpoter import single_prediction

class StartMonitorAPIView(APIView):

    def post(self, request):

        serializer = StartMonitorSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        video_url = (
            serializer.validated_data[
                "video_url"
            ]
        )

        video_id = extract_video_id(
            video_url
        )

        if not video_id:

            return Response(
                {
                    "error":
                        "Invalid YouTube URL or ID."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        api_key = settings.YOUTUBE_API_KEY

        try:

            video_info = fetch_video_info(
                api_key,
                video_id
            )

            live_chat_id = get_live_chat_id(
                api_key,
                video_id
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not live_chat_id:

            return Response(
                {
                    "error":
                        "This video does not have an active live chat."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({

            "video_id": video_id,

            "live_chat_id":
                live_chat_id,

            "video_info":
                video_info,

            "page_token": None,

            "message":
                "Live monitoring started."

        })

class PollMonitorAPIView(APIView):

    def post(self, request):

        serializer = PollMonitorSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        video_id = (
            serializer.validated_data[
                "video_id"
            ]
        )

        page_token = (
            serializer.validated_data.get(
                "page_token"
            )
        )

        api_key = settings.YOUTUBE_API_KEY

        try:

            live_chat_id = get_live_chat_id(
                api_key,
                video_id
            )

            if not live_chat_id:

                return Response(
                    {
                        "error":
                            "Live chat is no longer active."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = fetch_live_chat_messages(
                api_key,
                live_chat_id,
                page_token=page_token,
                max_results=50
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        analyzed_comments = []

        for message in result["messages"]:

            text = message["text"]

            try:

                prediction = single_prediction(
                    text
                )

                label = prediction[0]
                confidence = float(
                    prediction[1]
                )

            except Exception:

                label = "NEU"
                confidence = 0.0

            analyzed_comments.append({

                "id":
                    message["id"],

                "text":
                    text,

                "author":
                    message["author"],

                "published":
                    message["published"],

                "label":
                    label,

                "confidence":
                    round(
                        confidence,
                        4
                    ),

                "is_moderator":
                    message["is_moderator"],

                "is_owner":
                    message["is_owner"]

            })

        return Response({

            "comments":
                analyzed_comments,

            "next_page_token":
                result["next_page_token"],

            "polling_interval":
                result["polling_interval"]

        })

def monitor_page(request):
    return render(
        request,
        "youtube_monitor/monitor.html"
    )