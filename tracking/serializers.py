from rest_framework import serializers
from .models import WeightEntry

class WeightEntrySerializer(serializers.ModelSerializer):
    """Serializer for weight entry model"""
    class Meta:
        model = WeightEntry
        fields = ['id', 'weight', 'date', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class WeightHistorySerializer(serializers.Serializer):
    """Serializer for weight history response"""
    weight_history = WeightEntrySerializer(many=True)
    statistics = serializers.DictField()
    trend = serializers.DictField()
    projection = serializers.DictField()
