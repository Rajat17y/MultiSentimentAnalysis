from django.urls import path

app_name = "youtube_monitor"

from .views import(
    StartMonitorAPIView,
    PollMonitorAPIView,
    monitor_page
)

urlpatterns = [
    path(
        "",
        monitor_page,
        name="youtube-monitor"
    ),
    path(
        "api/start/",
        StartMonitorAPIView.as_view(),
        name="youtube-start"
    ),

    path(
        "api/poll/",
        PollMonitorAPIView.as_view(),
        name="youtube-poll"
    ),
]