from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class NutritionPlan(models.Model):
    """Model to store nutrition diet plan history"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="nutrition_plans"
    )
    input_parameters = models.JSONField()
    nutrition_result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Nutrition plans"

    def __str__(self):
        return f"Nutrition plan for {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
