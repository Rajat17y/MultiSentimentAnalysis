from django.shortcuts import render, get_object_or_404
from .models import AnalysisResult
from django.core.paginator import Paginator
from .utils import flatten_comments
import json
from django.http import JsonResponse
from ml_model.ModelImpoter import single_prediction

def landing(request):
    return render(
        request,
        "dashboard/landing.html"
    )

def home(request):
    return render(
        request,
        "dashboard/home.html"
    )

def results(request, analysis_id):

    analysis = get_object_or_404(
        AnalysisResult,
        id=analysis_id
    )

    return render(
        request,
        "dashboard/results.html",
        {
            "analysis": analysis,
            "statistics": analysis.statistics
        }
    )

def comments(request, analysis_id):

    analysis = get_object_or_404(
        AnalysisResult,
        id=analysis_id
    )

    comments_list = flatten_comments(
        analysis.results
    )

    platform = request.GET.get(
        "platform"
    )

    if platform:

        comments_list = [
            comment
            for comment in comments_list
            if comment["platform"] == platform
        ]

    paginator = Paginator(
        comments_list,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    return render(
        request,
        "dashboard/comments.html",
        {
            "analysis": analysis,
            "page_obj": page_obj,
            "selected_platform": platform,
        }
    )


def single_prediction_page(request):
    return render(
        request,
        "dashboard/single_pred.html"
    )


def single_prediction_api(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "error": "Only POST requests are allowed."
            },
            status=405
        )

    try:

        data = json.loads(
            request.body
        )

        text = data.get("text", "").strip()

        if not text:

            return JsonResponse(
                {
                    "error": "Text cannot be empty."
                },
                status=400
            )


        result = single_prediction(text)

        predicted_class = result[0]

        confidence = float(result[1])


        return JsonResponse(
            {
                "text": text,

                "sentiment":
                    predicted_class,

                "confidence":
                    confidence
            }
        )


    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "Invalid JSON."
            },
            status=400
        )


    except Exception as e:

        print(
            f"Prediction error: {e}"
        )

        return JsonResponse(
            {
                "error":
                    "Unable to analyze the text."
            },
            status=500
        )