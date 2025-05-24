from django.db import models

class ModelFeature(models.Model):
    """Model to store information about the recommendation model features"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    importance = models.FloatField(default=0.0, help_text="Feature importance score (0-1)")
    
    class Meta:
        ordering = ['-importance']
    
    def __str__(self):
        return self.name

class ModelCapability(models.Model):
    """Model to store information about the recommendation model capabilities"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class ModelMetadata(models.Model):
    """Model to store metadata about the recommendation model"""
    version = models.CharField(max_length=20)
    last_updated = models.DateField()
    accuracy = models.FloatField(help_text="Overall model accuracy (0-1)")
    description = models.TextField()
    
    class Meta:
        verbose_name_plural = "Model metadata"
    
    def __str__(self):
        return f"Model v{self.version} ({self.last_updated})"
