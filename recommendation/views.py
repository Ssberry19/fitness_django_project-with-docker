import os
import json
import numpy as np
from datetime import datetime
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import RecommendationInputSerializer, RecommendationOutputSerializer
from .models import RecommendationHistory

class MockFitnessRecommendationModel:
    """
    Mock implementation of the fitness recommendation model for development
    Will be replaced with actual model integration in production
    """
    def generate_recommendation(self, user_data):
        """Generate a mock recommendation based on user data"""
        # Calculate BMI
        height_m = user_data['height'] / 100
        weight_kg = user_data['weight']
        bmi = weight_kg / (height_m * height_m)
        bmi_category = self._get_bmi_category(bmi)
        
        # Determine recommendation components based on user data
        gender = user_data['gender']
        age = user_data['age']
        goal = user_data['goal']
        activity_level = user_data['activity_level']
        
        # Generate weekly structure based on goal and activity level
        weekly_structure = self._generate_weekly_structure(goal, activity_level)
        
        # Generate cardio training based on goal, activity level, and age
        cardio_training = self._generate_cardio_training(goal, activity_level, age)
        
        # Generate strength training based on gender, goal, and activity level
        strength_training = self._generate_strength_training(gender, goal, activity_level)
        
        # Generate progression plan
        progression_plan = self._generate_progression_plan(goal)
        
        # Generate BMI guidance
        bmi_guidance = self._generate_bmi_guidance(bmi, bmi_category, goal)
        
        # Generate age guidance
        age_guidance = self._generate_age_guidance(age)
        
        # Generate weight change guidance
        target_weight = user_data.get('target_weight', weight_kg)
        weight_change = self._generate_weight_change_guidance(weight_kg, target_weight, goal)
        
        # Generate cycle considerations for women
        cycle_considerations = ""
        if gender == 'F' and 'cycle_start_date' in user_data and user_data['cycle_start_date']:
            cycle_phase = self._determine_cycle_phase(user_data['cycle_start_date'])
            cycle_considerations = self._generate_cycle_considerations(cycle_phase)
        
        # Combine components into full recommendation
        components = {
            'weekly_structure': weekly_structure,
            'cardio_training': cardio_training,
            'strength_training': strength_training,
            'progression_plan': progression_plan,
            'bmi_guidance': bmi_guidance,
            'age_guidance': age_guidance,
            'weight_change': weight_change,
            'cycle_considerations': cycle_considerations
        }
        
        # Create personalized greeting
        greeting = f"**Personalized Training Plan** - {gender}/{age}/{user_data['height']}cm/{weight_kg:.1f}kg/BMI:{bmi:.1f}/{goal}/{activity_level}"
        
        # Combine components into full recommendation
        recommendation_parts = [greeting]
        
        if weekly_structure:
            recommendation_parts.append(f"**Weekly Structure:** {weekly_structure}")
        
        if cardio_training:
            recommendation_parts.append(f"**Cardio Training:** {cardio_training}")
        
        if strength_training:
            recommendation_parts.append(f"**Strength Training:** {strength_training}")
        
        if progression_plan:
            recommendation_parts.append(f"**Progression Plan:** {progression_plan}")
        
        if bmi_guidance:
            recommendation_parts.append(f"**Based on BMI ({bmi:.1f} - {bmi_category}):** {bmi_guidance}")
        
        if age_guidance:
            recommendation_parts.append(f"**Age-Specific Guidance ({self._get_age_group(age)}):** {age_guidance}")
        
        if weight_change:
            weight_change_kg = target_weight - weight_kg
            weight_change_pct = (weight_change_kg / weight_kg) * 100
            recommendation_parts.append(f"**Weight Change Goal:** {weight_change_pct:.1f}% {'' if weight_change_pct < 0 else '+'} ({weight_change_kg:.1f}kg). {weight_change}")
        
        if gender == 'F' and cycle_considerations:
            cycle_phase = self._determine_cycle_phase(user_data['cycle_start_date'])
            recommendation_parts.append(f"**Menstrual Cycle Considerations ({cycle_phase} phase):** {cycle_considerations}")
        
        # Join all parts
        full_recommendation = " ".join(recommendation_parts)
        
        return {
            'components': components,
            'full_recommendation': full_recommendation
        }
    
    def _get_bmi_category(self, bmi):
        """Get BMI category based on BMI value"""
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal weight"
        elif bmi < 30:
            return "overweight"
        elif bmi < 35:
            return "obesity class 1"
        elif bmi < 40:
            return "obesity class 2"
        else:
            return "obesity class 3"
    
    def _get_age_group(self, age):
        """Get age group description"""
        if age < 18:
            return "under 18"
        elif age < 31:
            return "18-30"
        elif age < 46:
            return "31-45"
        elif age < 61:
            return "46-60"
        else:
            return "over 60"
    
    def _determine_cycle_phase(self, cycle_start_date):
        """Determine menstrual cycle phase from cycle start date"""
        try:
            if isinstance(cycle_start_date, str):
                cycle_date = datetime.strptime(cycle_start_date, "%Y-%m-%d")
            else:
                cycle_date = cycle_start_date
                
            days_since = (datetime.now() - cycle_date).days
            
            if days_since < 5:
                return "menstrual"
            elif days_since < 14:
                return "follicular"
            elif days_since < 17:
                return "ovulatory"
            else:
                return "luteal"
        except (ValueError, TypeError):
            return "unknown"
    
    def _generate_weekly_structure(self, goal, activity_level):
        """Generate weekly training structure based on goal and activity level"""
        structures = {
            'weight_loss': {
                'sedentary': "3-4 days of cardio (20-30 min) with 2 days of full-body strength training. Focus on creating a calorie deficit through diet and exercise.",
                'light_activity': "3-4 days of cardio (30-40 min) with 2-3 days of strength training. Alternate between upper and lower body workouts.",
                'moderate_activity': "4-5 days of mixed cardio (30-45 min) with 3 days of strength training. Include HIIT sessions twice weekly.",
                'very_active': "5-6 days of varied training with 3 strength sessions, 2 HIIT sessions, and 1 longer cardio session. Include active recovery days."
            },
            'maintenance': {
                'sedentary': "2-3 days of cardio (20-30 min) with 2 days of strength training. Focus on consistency rather than intensity.",
                'light_activity': "3 days of cardio (20-30 min) with 2-3 days of strength training. Balance between cardio and resistance work.",
                'moderate_activity': "3-4 days of varied cardio with 3 days of strength training. Include flexibility work twice weekly.",
                'very_active': "4-5 days of mixed training with equal focus on strength, cardio, and mobility. Include one active recovery day."
            },
            'weight_gain': {
                'sedentary': "2 days of light cardio (15-20 min) with 3 days of strength training. Focus on progressive overload in strength sessions.",
                'light_activity': "2 days of moderate cardio with 3-4 days of hypertrophy-focused strength training. Emphasize major muscle groups.",
                'moderate_activity': "2-3 days of cardio (20-30 min) with 4 days of split strength training. Focus on compound movements.",
                'very_active': "2-3 days of cardio with 4-5 days of intensive strength training. Use a push/pull/legs split for maximum muscle stimulation."
            },
            'cutting': {
                'sedentary': "3-4 days of cardio (20-30 min) with 3 days of strength training. Maintain protein intake to preserve muscle mass.",
                'light_activity': "4 days of cardio (mix of HIIT and steady-state) with 3 days of strength training. Keep intensity high but reduce volume.",
                'moderate_activity': "5 days of varied cardio (including fasted morning sessions) with 3-4 days of strength training. Focus on maintaining strength.",
                'very_active': "5-6 days of training with 3 strength sessions, 2 HIIT sessions, and 1-2 steady-state cardio sessions. Carefully monitor recovery."
            }
        }
        
        return structures.get(goal, {}).get(activity_level, "3-4 days of mixed training with balanced cardio and strength work.")
    
    def _generate_cardio_training(self, goal, activity_level, age):
        """Generate cardio training recommendations based on goal, activity level, and age"""
        base_recommendations = {
            'weight_loss': {
                'sedentary': "Start with walking (20-30 min) at moderate pace (RPE 4-5/10). Gradually increase duration before intensity.",
                'light_activity': "Mix walking and jogging intervals. Add 1-2 HIIT sessions (10-15 min) weekly with 30s work/90s rest intervals.",
                'moderate_activity': "Include 2-3 HIIT sessions (15-20 min) weekly. Add steady-state cardio (30-40 min at RPE 6-7/10) on alternate days.",
                'very_active': "Varied cardio including HIIT (20 min, 40s work/80s rest), steady-state (40-50 min at RPE 7/10), and interval training."
            },
            'maintenance': {
                'sedentary': "Focus on consistent moderate cardio (20-30 min at RPE 5-6/10) 2-3 times weekly. Walking, cycling, or swimming recommended.",
                'light_activity': "Mix of moderate cardio (25-35 min at RPE 6/10) with one weekly interval session (alternating 2 min hard/2 min easy).",
                'moderate_activity': "Balanced approach with 2 moderate sessions (30-40 min at RPE 6-7/10) and 1-2 interval sessions weekly.",
                'very_active': "Varied cardio including one longer session (50-60 min), one HIIT session, and 1-2 moderate intensity sessions weekly."
            },
            'weight_gain': {
                'sedentary': "Limit cardio to 15-20 min sessions at moderate intensity (RPE 5/10), 2 times weekly to avoid excessive calorie burn.",
                'light_activity': "Short cardio sessions (20 min) at moderate intensity (RPE 5-6/10) to maintain cardiovascular health without hindering gains.",
                'moderate_activity': "2-3 cardio sessions weekly (20-30 min) at moderate intensity. Focus on maintaining conditioning without excessive duration.",
                'very_active': "Strategic cardio: 2-3 sessions (20-30 min) at moderate intensity plus one interval session to maintain conditioning."
            },
            'cutting': {
                'sedentary': "Mix of HIIT (10-15 min, 30s work/90s rest) and moderate steady-state cardio (25-30 min at RPE 6/10).",
                'light_activity': "3-4 cardio sessions weekly, alternating between HIIT (15-20 min) and steady-state (30-40 min at RPE 7/10).",
                'moderate_activity': "Strategic mix: morning fasted cardio (20-30 min at RPE 6/10) plus evening HIIT sessions (20 min) 2-3 times weekly.",
                'very_active': "Comprehensive approach: 2-3 HIIT sessions (20-25 min), 2 steady-state sessions (40 min at RPE 7/10), and 1 longer session (60 min)."
            }
        }
        
        # Get base recommendation
        base_rec = base_recommendations.get(goal, {}).get(activity_level, "Mix of moderate intensity cardio and interval training 3-4 times weekly.")
        
        # Adjust for age
        age_adjustments = {
            'under 18': "Keep intensity moderate and focus on enjoyable activities. Ensure proper form and technique before increasing intensity.",
            '18-30': "",  # No adjustment needed
            '31-45': "Monitor heart rate and ensure proper warm-up. Recovery between high-intensity sessions may need to be extended by 1 day.",
            '46-60': "Extend warm-up and cool-down periods. Consider reducing high-intensity work to 30s intervals with longer recovery periods.",
            'over 60': "Focus on low-impact activities like swimming, cycling, or elliptical. Extend warm-up to 10 minutes and keep RPE between 4-7/10."
        }
        
        age_group = self._get_age_group(age)
        age_adjustment = age_adjustments.get(age_group, "")
        
        if age_adjustment:
            return f"{base_rec} {age_adjustment}"
        return base_rec
    
    def _generate_strength_training(self, gender, goal, activity_level):
        """Generate strength training recommendations based on gender, goal, and activity level"""
        base_recommendations = {
            'weight_loss': {
                'sedentary': "Full-body circuit training 2 times weekly. 8-10 exercises, 2-3 sets, 12-15 reps with minimal rest between exercises.",
                'light_activity': "Full-body workouts 2-3 times weekly. Focus on compound movements (squats, push-ups, rows) with 3 sets of 12-15 reps.",
                'moderate_activity': "Upper/lower split 3 times weekly. 4-5 exercises per muscle group, 3 sets, 10-12 reps with moderate weights.",
                'very_active': "4-day split (push/pull/legs/core). 4-5 exercises per session, 3-4 sets, 10-12 reps. Include supersets to increase calorie burn."
            },
            'maintenance': {
                'sedentary': "Full-body workouts 2 times weekly. Basic compound movements, 2-3 sets, 10-12 reps with moderate weights.",
                'light_activity': "Full-body workouts 2-3 times weekly. Mix of compound and isolation exercises, 3 sets, 8-12 reps.",
                'moderate_activity': "3-day split (push/pull/legs). 3-4 exercises per muscle group, 3 sets, 8-12 reps with moderate to heavy weights.",
                'very_active': "4-day split with periodized approach. Alternate between strength phases (4-6 reps) and hypertrophy phases (8-12 reps)."
            },
            'weight_gain': {
                'sedentary': "Full-body workouts 3 times weekly. Focus on compound movements, 3-4 sets, 8-10 reps with progressive overload.",
                'light_activity': "Upper/lower split 3-4 times weekly. Emphasis on compound lifts, 4 sets, 6-10 reps with heavier weights.",
                'moderate_activity': "4-day split targeting major muscle groups. 4-5 exercises per session, 4 sets, 6-10 reps with heavy weights.",
                'very_active': "5-day body part split with emphasis on hypertrophy. 5-6 exercises per muscle group, 4 sets, 8-12 reps with controlled tempo."
            },
            'cutting': {
                'sedentary': "Full-body workouts 3 times weekly. Maintain weight but increase tempo, 3 sets, 10-12 reps with minimal rest.",
                'light_activity': "Upper/lower split 3-4 times weekly. Focus on maintaining strength, 3-4 sets, 8-10 reps with moderate to heavy weights.",
                'moderate_activity': "4-day split with emphasis on compound movements. 4 sets, 6-10 reps with heavy weights to preserve muscle mass.",
                'very_active': "5-day split with high volume. Mix of heavy compound movements (4-6 reps) and moderate isolation work (10-12 reps)."
            }
        }
        
        # Get base recommendation
        base_rec = base_recommendations.get(goal, {}).get(activity_level, "Balanced strength training 3 times weekly focusing on all major muscle groups.")
        
        # Gender-specific adjustments
        gender_adjustments = {
            'M': {
                'weight_loss': "Include metabolic resistance training circuits to maximize calorie burn.",
                'maintenance': "Balance upper and lower body work with equal emphasis on pushing and pulling movements.",
                'weight_gain': "Emphasize progressive overload on compound lifts like bench press, squats, and deadlifts.",
                'cutting': "Maintain heavy compound lifts while adjusting volume to account for reduced recovery capacity."
            },
            'F': {
                'weight_loss': "Include exercises that target multiple muscle groups simultaneously to maximize efficiency.",
                'maintenance': "Balance functional movements with targeted glute, core, and upper body exercises.",
                'weight_gain': "Focus on progressive overload while emphasizing glutes, legs, and balanced upper body development.",
                'cutting': "Maintain intensity on key lifts while incorporating more circuit-style training to preserve muscle."
            }
        }
        
        gender_adjustment = gender_adjustments.get(gender, {}).get(goal, "")
        
        if gender_adjustment:
            return f"{base_rec} {gender_adjustment}"
        return base_rec
    
    def _generate_progression_plan(self, goal):
        """Generate progression plan based on goal"""
        progression_plans = {
            'weight_loss': "Weeks 1-4: Focus on establishing consistent workout routine and proper form. Weeks 5-8: Increase workout duration by 5-10 minutes and add one HIIT session weekly. Weeks 9-12: Increase intensity of strength training and add complex movements.",
            'maintenance': "Weeks 1-4: Establish baseline strength and endurance levels. Weeks 5-8: Introduce periodization with alternating focus on strength and endurance. Weeks 9-12: Add variety through new exercises and training techniques to prevent plateaus.",
            'weight_gain': "Weeks 1-4: Focus on perfecting form on key compound lifts. Weeks 5-8: Implement progressive overload by increasing weight 5-10% on main lifts. Weeks 9-12: Increase training volume and add advanced techniques like drop sets and rest-pause sets.",
            'cutting': "Weeks 1-4: Maintain current training volume while gradually reducing caloric intake. Weeks 5-8: Increase cardio frequency while maintaining strength training intensity. Weeks 9-12: Implement strategic refeeds and adjust training split to maintain performance."
        }
        
        return progression_plans.get(goal, "Weeks 1-4: Establish baseline fitness. Weeks 5-8: Increase intensity and duration gradually. Weeks 9-12: Implement advanced techniques specific to your goals.")
    
    def _generate_bmi_guidance(self, bmi, bmi_category, goal):
        """Generate BMI-specific guidance"""
        bmi_guidance = {
            'underweight': {
                'weight_loss': "With your BMI below 18.5, weight loss is not recommended. Consider shifting your goal to weight gain or maintenance with a focus on building lean muscle.",
                'maintenance': "With your BMI below 18.5, focus on nutrient-dense foods and sufficient protein intake to support healthy body composition while maintaining weight.",
                'weight_gain': "With your BMI below 18.5, focus on gradual weight gain (0.5-1 lb/week) through strength training and caloric surplus from nutrient-dense foods.",
                'cutting': "With your BMI below 18.5, cutting is not recommended. Consider focusing on building muscle first before attempting to reduce body fat percentage."
            },
            'normal weight': {
                'weight_loss': "With your BMI in the normal range, focus on body composition changes rather than significant weight loss. Emphasize strength training to maintain muscle.",
                'maintenance': "Your BMI is in the healthy range. Focus on performance goals and body composition rather than weight changes.",
                'weight_gain': "With your BMI in the normal range, focus on lean muscle gain through progressive strength training and moderate caloric surplus.",
                'cutting': "With your BMI in the normal range, focus on gradual fat loss while preserving muscle mass through high protein intake and strength training."
            },
            'overweight': {
                'weight_loss': "With your BMI indicating overweight status, aim for gradual weight loss (1-2 lbs/week) through combined dietary changes and increased physical activity.",
                'maintenance': "Before maintaining your current weight, consider if a weight loss phase would benefit your health, as your BMI indicates overweight status.",
                'weight_gain': "With your BMI indicating overweight status, focus on recomposition (gaining muscle while losing fat) rather than overall weight gain.",
                'cutting': "With your BMI indicating overweight status, a cutting phase is appropriate. Focus on preserving muscle while creating a moderate caloric deficit."
            },
            'obesity class 1': {
                'weight_loss': "With your BMI indicating obesity, focus on consistent, moderate weight loss (1-2 lbs/week) through sustainable dietary changes and gradually increasing activity.",
                'maintenance': "With your BMI indicating obesity, consider if a weight loss phase would be more beneficial for your health before maintaining current weight.",
                'weight_gain': "With your BMI indicating obesity, weight gain is not recommended. Consider shifting your goal to weight loss for health benefits.",
                'cutting': "With your BMI indicating obesity, focus on overall weight loss rather than a traditional cutting phase. Emphasize sustainable lifestyle changes."
            },
            'obesity class 2': {
                'weight_loss': "With your BMI indicating obesity class 2, prioritize consistent weight loss through medical supervision. Focus on low-impact activities and dietary changes.",
                'maintenance': "With your BMI indicating obesity class 2, weight loss is recommended for health benefits rather than weight maintenance.",
                'weight_gain': "With your BMI indicating obesity class 2, weight gain is not recommended. Please consult with a healthcare provider about appropriate fitness goals.",
                'cutting': "With your BMI indicating obesity class 2, focus on overall weight loss for health rather than aesthetic cutting. Consult with healthcare providers."
            },
            'obesity class 3': {
                'weight_loss': "With your BMI indicating obesity class 3, work with healthcare providers to develop a medically supervised weight loss plan with appropriate exercise modifications.",
                'maintenance': "With your BMI indicating obesity class 3, weight loss is strongly recommended for health benefits rather than weight maintenance.",
                'weight_gain': "With your BMI indicating obesity class 3, weight gain is not recommended. Please consult with healthcare providers about appropriate fitness goals.",
                'cutting': "With your BMI indicating obesity class 3, traditional cutting approaches are not appropriate. Work with healthcare providers on medically supervised weight loss."
            }
        }
        
        # Handle cases where BMI category might not be in our predefined categories
        if bmi_category not in bmi_guidance:
            if bmi >= 30:
                bmi_category = 'obesity class 1'
            elif bmi >= 25:
                bmi_category = 'overweight'
            elif bmi >= 18.5:
                bmi_category = 'normal weight'
            else:
                bmi_category = 'underweight'
        
        return bmi_guidance.get(bmi_category, {}).get(goal, f"With your BMI of {bmi:.1f}, focus on balanced nutrition and consistent exercise appropriate for your fitness level.")
    
    def _generate_age_guidance(self, age):
        """Generate age-specific guidance"""
        age_guidance = {
            'under 18': "Focus on developing proper exercise technique and consistency. Emphasize bodyweight exercises and moderate resistance training. Ensure adequate nutrition to support growth and development.",
            '18-30': "This is an optimal time for building strength and fitness habits. Focus on progressive overload in strength training and developing cardiovascular endurance. Recovery capacity is typically high.",
            '31-45': "Balance intensity with recovery as metabolism begins to change. Focus on maintaining muscle mass through consistent strength training. Monitor joint health and incorporate more mobility work.",
            '46-60': "Emphasize strength training to combat natural muscle loss. Focus on functional movements that support daily activities. Include more dedicated warm-up time and recovery between intense sessions.",
            'over 60': "Prioritize strength and balance training to maintain independence. Focus on low-impact activities and proper form. Include specific exercises for bone density and joint health. Extend warm-up and cool-down periods."
        }
        
        age_group = self._get_age_group(age)
        return age_guidance.get(age_group, "Focus on consistency and gradual progression appropriate for your age and fitness level.")
    
    def _generate_weight_change_guidance(self, current_weight, target_weight, goal):
        """Generate weight change guidance based on current weight, target weight, and goal"""
        weight_diff = target_weight - current_weight
        weight_change_pct = (weight_diff / current_weight) * 100
        
        if abs(weight_change_pct) < 1:
            return "Your target weight is very close to your current weight. Focus on body composition changes rather than weight changes."
        
        if weight_diff > 0:  # Weight gain
            if weight_diff > 0.2 * current_weight:  # More than 20% gain
                return "Your target weight represents a significant increase. Consider setting intermediate goals and focusing on gradual, healthy weight gain of 0.5-1 lb per week."
            else:
                return f"To reach your target weight gain of {weight_diff:.1f}kg, focus on a moderate caloric surplus (300-500 calories/day) and progressive strength training. Aim for 0.5-1 lb of gain per week."
        else:  # Weight loss
            if abs(weight_diff) > 0.2 * current_weight:  # More than 20% loss
                return "Your target weight represents a significant decrease. Consider setting intermediate goals and focusing on gradual, sustainable weight loss of 1-2 lbs per week."
            else:
                return f"To reach your target weight loss of {abs(weight_diff):.1f}kg, create a moderate caloric deficit (500 calories/day) through diet and exercise. Aim for 1-2 lbs of loss per week."
    
    def _generate_cycle_considerations(self, cycle_phase):
        """Generate menstrual cycle considerations based on cycle phase"""
        cycle_guidance = {
            'menstrual': "During your menstrual phase, energy levels may be lower. Focus on lighter intensity workouts and prioritize recovery. Gentle yoga, walking, and light strength training are ideal. Iron-rich foods can help combat fatigue.",
            'follicular': "During your follicular phase, energy levels typically increase. This is an optimal time for higher intensity workouts and strength training. Take advantage of potentially increased strength and endurance during this phase.",
            'ovulatory': "During your ovulatory phase, energy and strength may peak. This is an excellent time for challenging workouts, personal records, and high-intensity training. Monitor hydration as body temperature may be slightly elevated.",
            'luteal': "During your luteal phase, you may experience decreased energy and increased core temperature. Focus on moderate intensity workouts, adjust expectations, and increase cooling strategies. Emphasize protein intake to manage cravings.",
            'unknown': "Consider tracking your menstrual cycle to optimize training. Different phases can affect energy levels, strength, and recovery capacity, allowing for strategic training adjustments."
        }
        
        return cycle_guidance.get(cycle_phase, "Consider how your menstrual cycle affects your energy and performance. Adjust training intensity based on how you feel throughout your cycle.")


class RecommendationAPIView(APIView):
    """API view for fitness recommendations"""
    # permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Generate fitness recommendation based on user data"""
        serializer = RecommendationInputSerializer(data=request.data)
        if serializer.is_valid():
            # Get validated data
            user_data = serializer.validated_data
            
            # Initialize recommendation model
            # In production, this would load the actual ML model
            model = MockFitnessRecommendationModel()
            
            try:
                # Generate recommendation
                recommendation = model.generate_recommendation(user_data)
                
                # Validate output
                output_serializer = RecommendationOutputSerializer(data=recommendation)
                if output_serializer.is_valid():
                    # Save recommendation history
                    RecommendationHistory.objects.create(
                        user=request.user,
                        input_parameters=user_data,
                        recommendation_result=recommendation
                    )
                    
                    return Response(output_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(output_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response(
                    {"error": f"Error generating recommendation: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
