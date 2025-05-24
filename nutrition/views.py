import math
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import NutritionInputSerializer, NutritionOutputSerializer
from .models import NutritionPlan

class MockNutritionDietGenerator:
    """
    Mock implementation of the nutrition diet generator
    Will be replaced with actual model integration in production
    """
    def generate_nutrition_plan(self, user_data):
        """Generate a mock nutrition plan based on user data"""
        # Calculate BMI and BMR
        height_m = user_data['height'] / 100
        weight_kg = user_data['weight']
        age = user_data['age']
        gender = user_data['gender']
        goal = user_data['goal']
        activity_level = user_data['activity_level']
        dietary_restrictions = user_data.get('dietary_restrictions', [])
        allergies = user_data.get('allergies', [])
        preferred_cuisine = user_data.get('preferred_cuisine', '')
        
        # Calculate BMI
        bmi = weight_kg / (height_m * height_m)
        
        # Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
        if gender == 'M':
            bmr = 10 * weight_kg + 6.25 * user_data['height'] - 5 * age + 5
        else:  # gender == 'F'
            bmr = 10 * weight_kg + 6.25 * user_data['height'] - 5 * age - 161
        
        # Apply activity multiplier
        activity_multipliers = {
            'sedentary': 1.2,
            'light_activity': 1.375,
            'moderate_activity': 1.55,
            'very_active': 1.725
        }
        
        tdee = bmr * activity_multipliers.get(activity_level, 1.2)  # TDEE = Total Daily Energy Expenditure
        
        # Adjust calories based on goal
        goal_adjustments = {
            'weight_loss': -500,  # Caloric deficit
            'maintenance': 0,     # Maintain current weight
            'weight_gain': 500,   # Caloric surplus
            'cutting': -350       # Moderate deficit to preserve muscle
        }
        
        daily_calories = math.ceil(tdee + goal_adjustments.get(goal, 0))
        
        # Ensure minimum healthy calorie intake
        min_calories = 1200 if gender == 'F' else 1500
        daily_calories = max(daily_calories, min_calories)
        
        # Calculate macronutrients based on goal
        macronutrient_ratios = {
            'weight_loss': {'protein': 0.40, 'carbs': 0.30, 'fats': 0.30},
            'maintenance': {'protein': 0.30, 'carbs': 0.40, 'fats': 0.30},
            'weight_gain': {'protein': 0.30, 'carbs': 0.45, 'fats': 0.25},
            'cutting': {'protein': 0.45, 'carbs': 0.25, 'fats': 0.30}
        }
        
        ratios = macronutrient_ratios.get(goal, {'protein': 0.30, 'carbs': 0.40, 'fats': 0.30})
        
        # Calculate grams of each macronutrient
        protein_calories = daily_calories * ratios['protein']
        carb_calories = daily_calories * ratios['carbs']
        fat_calories = daily_calories * ratios['fats']
        
        protein_grams = math.ceil(protein_calories / 4)  # 4 calories per gram of protein
        carb_grams = math.ceil(carb_calories / 4)        # 4 calories per gram of carbs
        fat_grams = math.ceil(fat_calories / 9)          # 9 calories per gram of fat
        
        macronutrients = {
            'protein': protein_grams,
            'carbs': carb_grams,
            'fats': fat_grams,
            'protein_pct': round(ratios['protein'] * 100),
            'carbs_pct': round(ratios['carbs'] * 100),
            'fats_pct': round(ratios['fats'] * 100)
        }
        
        # Generate meal plan
        meal_plan = self._generate_meal_plan(
            daily_calories, 
            macronutrients, 
            dietary_restrictions, 
            allergies, 
            preferred_cuisine
        )
        
        # Calculate hydration recommendation
        hydration = self._calculate_hydration(weight_kg, activity_level)
        
        return {
            'daily_calories': daily_calories,
            'macronutrients': macronutrients,
            'meal_plan': meal_plan,
            'hydration': hydration
        }
    
    def _generate_meal_plan(self, daily_calories, macronutrients, dietary_restrictions, allergies, preferred_cuisine):
        """Generate a weekly meal plan based on calculated requirements"""
        # Mock meal plan generation
        # In a real implementation, this would use a more sophisticated algorithm
        # or integrate with a nutrition API
        
        # Adjust meal options based on dietary restrictions
        is_vegetarian = 'vegetarian' in dietary_restrictions
        is_vegan = 'vegan' in dietary_restrictions
        is_gluten_free = 'gluten-free' in dietary_restrictions
        is_dairy_free = 'dairy-free' in dietary_restrictions
        
        # Create meal distribution
        if daily_calories < 1600:
            meal_distribution = {'breakfast': 0.25, 'lunch': 0.35, 'dinner': 0.30, 'snacks': 0.10}
        elif daily_calories < 2200:
            meal_distribution = {'breakfast': 0.25, 'lunch': 0.30, 'dinner': 0.30, 'snacks': 0.15}
        else:
            meal_distribution = {'breakfast': 0.20, 'lunch': 0.30, 'dinner': 0.30, 'snacks': 0.20}
        
        # Generate sample meals for each day of the week
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_plan = {}
        
        for day in days:
            daily_meals = {}
            
            # Breakfast options
            breakfast_options = [
                "Oatmeal with berries and nuts",
                "Greek yogurt with granola and fruit",
                "Whole grain toast with avocado and eggs",
                "Protein smoothie with spinach and banana",
                "Quinoa breakfast bowl with vegetables"
            ]
            
            if is_vegan:
                breakfast_options = [
                    "Oatmeal with berries and nuts",
                    "Vegan protein smoothie with spinach and banana",
                    "Whole grain toast with avocado and tofu scramble",
                    "Chia seed pudding with almond milk and fruit",
                    "Quinoa breakfast bowl with vegetables"
                ]
            elif is_vegetarian and not is_vegan:
                breakfast_options = [
                    "Oatmeal with berries and nuts",
                    "Greek yogurt with granola and fruit",
                    "Whole grain toast with avocado and eggs",
                    "Vegetarian protein smoothie with spinach and banana",
                    "Quinoa breakfast bowl with vegetables"
                ]
            
            if is_gluten_free:
                breakfast_options = [option for option in breakfast_options if "toast" not in option.lower() and "granola" not in option.lower()] + [
                    "Gluten-free oatmeal with berries and nuts",
                    "Rice porridge with fruit and seeds"
                ]
            
            if is_dairy_free:
                breakfast_options = [option for option in breakfast_options if "yogurt" not in option.lower() and "milk" not in option.lower()] + [
                    "Coconut yogurt with fruit and seeds",
                    "Almond milk smoothie with protein powder"
                ]
            
            # Lunch options
            lunch_options = [
                "Grilled chicken salad with mixed greens",
                "Turkey and avocado wrap with vegetables",
                "Quinoa bowl with roasted vegetables and feta",
                "Tuna salad with whole grain crackers",
                "Lentil soup with whole grain bread"
            ]
            
            if is_vegan:
                lunch_options = [
                    "Chickpea salad with mixed greens and tahini dressing",
                    "Hummus and vegetable wrap",
                    "Quinoa bowl with roasted vegetables and tofu",
                    "Lentil soup with whole grain bread",
                    "Buddha bowl with brown rice and tempeh"
                ]
            elif is_vegetarian and not is_vegan:
                lunch_options = [
                    "Greek salad with feta cheese",
                    "Vegetable and cheese wrap",
                    "Quinoa bowl with roasted vegetables and feta",
                    "Lentil soup with whole grain bread",
                    "Caprese sandwich with mozzarella and tomato"
                ]
            
            if is_gluten_free:
                lunch_options = [option for option in lunch_options if "wrap" not in option.lower() and "bread" not in option.lower() and "crackers" not in option.lower()] + [
                    "Gluten-free wrap with protein and vegetables",
                    "Rice bowl with protein and vegetables"
                ]
            
            if is_dairy_free:
                lunch_options = [option for option in lunch_options if "cheese" not in option.lower() and "feta" not in option.lower()] + [
                    "Avocado and vegetable salad with olive oil dressing",
                    "Dairy-free pesto pasta with vegetables"
                ]
            
            # Dinner options
            dinner_options = [
                "Grilled salmon with roasted vegetables and quinoa",
                "Lean beef stir-fry with brown rice",
                "Baked chicken with sweet potato and broccoli",
                "Turkey meatballs with whole wheat pasta and marinara",
                "Shrimp and vegetable curry with brown rice"
            ]
            
            if is_vegan:
                dinner_options = [
                    "Lentil and vegetable curry with brown rice",
                    "Stir-fried tofu with vegetables and quinoa",
                    "Chickpea and vegetable stew",
                    "Vegan chili with mixed beans",
                    "Stuffed bell peppers with quinoa and vegetables"
                ]
            elif is_vegetarian and not is_vegan:
                dinner_options = [
                    "Vegetable curry with paneer and brown rice",
                    "Eggplant parmesan with whole wheat pasta",
                    "Black bean and vegetable enchiladas",
                    "Vegetarian chili with mixed beans",
                    "Stuffed bell peppers with quinoa and cheese"
                ]
            
            if is_gluten_free:
                dinner_options = [option for option in dinner_options if "pasta" not in option.lower() and "wheat" not in option.lower()] + [
                    "Gluten-free pasta with protein and vegetables",
                    "Stuffed acorn squash with protein and rice"
                ]
            
            if is_dairy_free:
                dinner_options = [option for option in dinner_options if "cheese" not in option.lower() and "parmesan" not in option.lower()] + [
                    "Coconut curry with protein and vegetables",
                    "Olive oil and herb marinated protein with vegetables"
                ]
            
            # Snack options
            snack_options = [
                "Apple with almond butter",
                "Greek yogurt with berries",
                "Protein bar",
                "Mixed nuts and dried fruit",
                "Hummus with vegetable sticks"
            ]
            
            if is_vegan:
                snack_options = [
                    "Apple with almond butter",
                    "Vegan protein bar",
                    "Mixed nuts and dried fruit",
                    "Hummus with vegetable sticks",
                    "Roasted chickpeas"
                ]
            elif is_vegetarian and not is_vegan:
                snack_options = [
                    "Apple with almond butter",
                    "Greek yogurt with berries",
                    "Vegetarian protein bar",
                    "Mixed nuts and dried fruit",
                    "Hummus with vegetable sticks"
                ]
            
            if is_gluten_free:
                snack_options = [option for option in snack_options if "bar" not in option.lower()] + [
                    "Gluten-free protein bar",
                    "Rice cakes with nut butter"
                ]
            
            if is_dairy_free:
                snack_options = [option for option in snack_options if "yogurt" not in option.lower()] + [
                    "Coconut yogurt with berries",
                    "Dairy-free smoothie"
                ]
            
            # Select meals for the day
            import random
            daily_meals = {
                'breakfast': random.choice(breakfast_options),
                'lunch': random.choice(lunch_options),
                'dinner': random.choice(dinner_options),
                'snacks': random.choice(snack_options)
            }
            
            # Add calorie distribution
            for meal, percentage in meal_distribution.items():
                meal_calories = round(daily_calories * percentage)
                daily_meals[f"{meal}_calories"] = meal_calories
            
            weekly_plan[day] = daily_meals
        
        return weekly_plan
    
    def _calculate_hydration(self, weight_kg, activity_level):
        """Calculate daily water intake recommendation"""
        # Base recommendation: 30-35 ml per kg of body weight
        base_hydration_ml = weight_kg * 33
        
        # Adjust based on activity level
        activity_adjustments = {
            'sedentary': 0,
            'light_activity': 300,
            'moderate_activity': 600,
            'very_active': 1000
        }
        
        total_hydration_ml = base_hydration_ml + activity_adjustments.get(activity_level, 0)
        
        # Convert to liters for easier understanding
        total_hydration_liters = round(total_hydration_ml / 1000, 1)
        
        return f"Drink approximately {total_hydration_liters} liters of water daily. Increase intake during exercise and hot weather."


class NutritionAPIView(APIView):
    """API view for nutrition diet plans"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Generate nutrition diet plan based on user data"""
        serializer = NutritionInputSerializer(data=request.data)
        if serializer.is_valid():
            # Get validated data
            user_data = serializer.validated_data
            
            # Initialize nutrition diet generator
            # In production, this would use a more sophisticated model
            generator = MockNutritionDietGenerator()
            
            try:
                # Generate nutrition plan
                nutrition_plan = generator.generate_nutrition_plan(user_data)
                
                # Validate output
                output_serializer = NutritionOutputSerializer(data=nutrition_plan)
                if output_serializer.is_valid():
                    # Save nutrition plan history
                    NutritionPlan.objects.create(
                        user=request.user,
                        input_parameters=user_data,
                        nutrition_result=nutrition_plan
                    )
                    
                    return Response(output_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(output_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response(
                    {"error": f"Error generating nutrition plan: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
