import os
import json
from datetime import datetime
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import ModelFeature, ModelCapability, ModelMetadata
from .serializers import ModelFeaturesResponseSerializer

class ModelFeaturesAPIView(APIView):
    """API view for model features and capabilities"""
    permission_classes = [AllowAny]  # Allow public access to model information
    
    def get(self, request):
        """Get model features, capabilities, and metadata"""
        # Try to get model metadata from database
        try:
            metadata = ModelMetadata.objects.latest('last_updated')
            model_version = metadata.version
            last_updated = metadata.last_updated
        except ModelMetadata.DoesNotExist:
            # If not in database, use default values
            model_version = "1.0.0"
            last_updated = datetime.now().date()
        
        # Get features from database or use defaults
        features = list(ModelFeature.objects.all())
        if not features:
            # Create default features if none exist
            default_features = self._get_default_features()
            features = default_features
        
        # Get capabilities from database or use defaults
        capabilities = list(ModelCapability.objects.all())
        if not capabilities:
            # Create default capabilities if none exist
            default_capabilities = self._get_default_capabilities()
            capabilities = default_capabilities
        
        # Get accuracy metrics from model config or use defaults
        accuracy_metrics = self._get_accuracy_metrics()
        
        # Prepare response data
        response_data = {
            'model_version': model_version,
            'features': features,
            'capabilities': capabilities,
            'accuracy_metrics': accuracy_metrics,
            'last_updated': last_updated
        }
        
        # Serialize and return response
        serializer = ModelFeaturesResponseSerializer(response_data)
        return Response(serializer.data)
    
    def _get_default_features(self):
        """Get default model features if not in database"""
        default_features = [
            ModelFeature(
                name="Gender",
                description="User's gender (male or female) affects exercise recommendations and caloric needs",
                importance=0.85
            ),
            ModelFeature(
                name="Age",
                description="User's age influences exercise intensity, recovery needs, and training focus",
                importance=0.80
            ),
            ModelFeature(
                name="Height",
                description="Used for BMI calculation and body proportion considerations",
                importance=0.65
            ),
            ModelFeature(
                name="Weight",
                description="Current weight used for BMI, caloric needs, and progress tracking",
                importance=0.90
            ),
            ModelFeature(
                name="BMI",
                description="Body Mass Index calculated from height and weight, used for health risk assessment",
                importance=0.75
            ),
            ModelFeature(
                name="Fitness Goal",
                description="Primary goal (weight loss, maintenance, weight gain, cutting) determines overall program structure",
                importance=0.95
            ),
            ModelFeature(
                name="Activity Level",
                description="Current activity level affects caloric needs and exercise prescription",
                importance=0.85
            ),
            ModelFeature(
                name="Target Weight",
                description="Goal weight used for progress projection and program adjustment",
                importance=0.70
            ),
            ModelFeature(
                name="Menstrual Cycle",
                description="For women, cycle phase affects energy levels, recovery, and training optimization",
                importance=0.60
            )
        ]
        
        # Save default features to database
        for feature in default_features:
            feature.save()
        
        return default_features
    
    def _get_default_capabilities(self):
        """Get default model capabilities if not in database"""
        default_capabilities = [
            ModelCapability(
                name="Weekly Training Structure",
                description="Generates personalized weekly workout schedules based on goals and availability"
            ),
            ModelCapability(
                name="Cardio Training Recommendations",
                description="Provides specific cardio exercise recommendations with intensity and duration"
            ),
            ModelCapability(
                name="Strength Training Programs",
                description="Creates targeted strength training programs with exercise selection and progression"
            ),
            ModelCapability(
                name="BMI-Specific Guidance",
                description="Offers health and fitness guidance specific to user's BMI category"
            ),
            ModelCapability(
                name="Age-Appropriate Recommendations",
                description="Adjusts recommendations based on age-related considerations and limitations"
            ),
            ModelCapability(
                name="Weight Change Projections",
                description="Projects weight change timelines based on current metrics and goals"
            ),
            ModelCapability(
                name="Menstrual Cycle Optimization",
                description="For women, provides training adjustments based on menstrual cycle phase"
            ),
            ModelCapability(
                name="Progression Planning",
                description="Creates long-term progression plans with appropriate intensity increases"
            )
        ]
        
        # Save default capabilities to database
        for capability in default_capabilities:
            capability.save()
        
        return default_capabilities
    
    def _get_accuracy_metrics(self):
        """Get model accuracy metrics from config or use defaults"""
        # Try to load from config file
        config_path = os.path.join(settings.ML_MODEL_DIR, 'model_metrics.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Return default metrics if config not available
        return {
            'overall_accuracy': 0.89,
            'recommendation_precision': 0.92,
            'user_satisfaction': 0.87,
            'component_accuracy': {
                'weekly_structure': 0.91,
                'cardio_training': 0.88,
                'strength_training': 0.90,
                'progression_plan': 0.85,
                'bmi_guidance': 0.93,
                'age_guidance': 0.89,
                'weight_change': 0.86,
                'cycle_considerations': 0.82
            }
        }
