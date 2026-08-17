from .models import AnalysisResult

def flatten_comments(results):

    comments = []

    for platform, platform_comments in results.items():

        for comment_data in platform_comments:

            comments.append({
                "platform": platform,
                "comment": comment_data[0],
                "sentiment": comment_data[1],
                "confidence": comment_data[2],
            })

    return comments

def cleanup_old_analyses():

    old_ids = list(
        AnalysisResult.objects
        .order_by("-created_at")
        .values_list("id", flat=True)[100:]
    )

    if old_ids:
        AnalysisResult.objects.filter(
            id__in=old_ids
        ).delete()