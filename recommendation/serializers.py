from rest_framework import serializers

class RecommendationInputSerializer(serializers.Serializer):
    """Serializer for fitness recommendation input parameters"""
    gender = serializers.ChoiceField(choices=['M', 'F'])
    age = serializers.IntegerField(min_value=1, max_value=120)
    height = serializers.FloatField(min_value=50, max_value=250)  # cm
    weight = serializers.FloatField(min_value=20, max_value=300)  # kg
    goal = serializers.ChoiceField(
        choices=['weight_loss', 'maintenance', 'weight_gain', 'cutting']
    )
    activity_level = serializers.ChoiceField(
        choices=['sedentary', 'light_activity', 'moderate_activity', 'very_active']
    )
    target_weight = serializers.FloatField(min_value=20, max_value=300, required=False)  # kg
    cycle_start_date = serializers.DateField(required=False)

class RecommendationOutputSerializer(serializers.Serializer):
    """Serializer for fitness recommendation output"""
    full_recommendation = serializers.CharField()
    components = serializers.DictField(child=serializers.CharField(allow_blank=True))
