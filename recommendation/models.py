from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class RecommendationHistory(models.Model):
    """Model to store fitness recommendation history"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fitness_recommendations"
    )
    input_parameters = models.JSONField()
    recommendation_result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Recommendation histories"

    def __str__(self):
        return f"Recommendation for {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
