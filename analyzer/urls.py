from django.urls import path
from .views import SentimentAPI

urlpatterns = [
    path(
        "predict/",
        SentimentAPI.as_view(),
        name="sentiment-predict"
    ),
]