from django.urls import include,path
from .import views

urlpatterns = [
    path(
        "",
        views.landing,
        name="landing"
    ),
    path(
        "Multi",
        views.home,
        name="home"
    ),

    path(
        "results/<int:analysis_id>/",
        views.results,
        name="results"
    ),

    path(
        "comments/<int:analysis_id>/",
        views.comments,
        name="comments"
    ),
    path(
        "single/",
        views.single_prediction_page,
        name="single_prediction"
    ),

    path(
        "single/predict/",
        views.single_prediction_api,
        name="single_prediction_api"
    ),
]