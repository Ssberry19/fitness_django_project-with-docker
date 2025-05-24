from rest_framework import serializers
from .models import ModelFeature, ModelCapability, ModelMetadata

class ModelFeatureSerializer(serializers.ModelSerializer):
    """Serializer for model features"""
    class Meta:
        model = ModelFeature
        fields = ['name', 'description', 'importance']

class ModelCapabilitySerializer(serializers.ModelSerializer):
    """Serializer for model capabilities"""
    class Meta:
        model = ModelCapability
        fields = ['name', 'description']

class ModelMetadataSerializer(serializers.ModelSerializer):
    """Serializer for model metadata"""
    class Meta:
        model = ModelMetadata
        fields = ['version', 'last_updated', 'accuracy', 'description']

class ModelFeaturesResponseSerializer(serializers.Serializer):
    """Serializer for the complete model features response"""
    model_version = serializers.CharField()
    features = ModelFeatureSerializer(many=True)
    capabilities = ModelCapabilitySerializer(many=True)
    accuracy_metrics = serializers.DictField()
    last_updated = serializers.DateField()
