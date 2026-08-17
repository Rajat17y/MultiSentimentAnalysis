from django.db import models

class AnalysisResult(models.Model):
    topic = models.CharField(
        max_length=255
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    results = models.JSONField()
    statistics = models.JSONField()

    def __str__(self):
        return self.topic