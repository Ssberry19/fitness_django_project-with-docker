from rest_framework import serializers

class NutritionInputSerializer(serializers.Serializer):
    """Serializer for nutrition diet plan input parameters"""
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
    dietary_restrictions = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )
    allergies = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )
    preferred_cuisine = serializers.CharField(max_length=50, required=False, allow_blank=True)

class NutritionOutputSerializer(serializers.Serializer):
    """Serializer for nutrition diet plan output"""
    daily_calories = serializers.IntegerField()
    macronutrients = serializers.DictField(child=serializers.FloatField())
    meal_plan = serializers.DictField()
    hydration = serializers.CharField()
