from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class WeightEntry(models.Model):
    """Model to store user weight tracking data"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="weight_entries"
    )
    weight = models.FloatField(help_text="Weight in kg")
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Weight entries"
        # Ensure each user can only have one weight entry per date
        unique_together = ["user", "date"]

    def __str__(self):
        return f"{self.user.username}: {self.weight}kg on {self.date}"
