# Fitness Recommendation API Documentation

## Overview
This Django application provides a comprehensive API for fitness recommendations, nutrition planning, weight tracking, and model information. The application integrates with a deep learning model to provide personalized fitness recommendations based on user data.

## API Endpoints

### 1. Fitness Recommendation API
**Endpoint:** `/api/recommendation/`  
**Method:** POST  
**Authentication:** Required  

**Request Body:**
```json
{
  "gender": "M",
  "age": 30,
  "height": 180,
  "weight": 80,
  "goal": "weight_loss",
  "activity_level": "moderate_activity",
  "target_weight": 75,
  "cycle_start_date": null
}
```

**Parameters:**
- `gender`: String, either "M" or "F"
- `age`: Integer, age in years
- `height`: Float, height in cm
- `weight`: Float, weight in kg
- `goal`: String, one of "weight_loss", "maintenance", "weight_gain", "cutting"
- `activity_level`: String, one of "sedentary", "light_activity", "moderate_activity", "very_active"
- `target_weight`: Float, target weight in kg (optional)
- `cycle_start_date`: String, date of last menstrual cycle start in YYYY-MM-DD format (optional, for women only)

**Response:**
```json
{
  "full_recommendation": "Personalized training plan text...",
  "components": {
    "weekly_structure": "Weekly structure text...",
    "cardio_training": "Cardio training text...",
    "strength_training": "Strength training text...",
    "progression_plan": "Progression plan text...",
    "bmi_guidance": "BMI guidance text...",
    "age_guidance": "Age guidance text...",
    "weight_change": "Weight change text...",
    "cycle_considerations": "Cycle considerations text..."
  }
}
```

### 2. Nutrition Diet API
**Endpoint:** `/api/nutrition/`  
**Method:** POST  
**Authentication:** Required  

**Request Body:**
```json
{
  "gender": "F",
  "age": 28,
  "height": 165,
  "weight": 65,
  "goal": "maintenance",
  "activity_level": "light_activity",
  "dietary_restrictions": ["vegetarian", "gluten-free"],
  "allergies": ["nuts"],
  "preferred_cuisine": "mediterranean"
}
```

**Parameters:**
- `gender`: String, either "M" or "F"
- `age`: Integer, age in years
- `height`: Float, height in cm
- `weight`: Float, weight in kg
- `goal`: String, one of "weight_loss", "maintenance", "weight_gain", "cutting"
- `activity_level`: String, one of "sedentary", "light_activity", "moderate_activity", "very_active"
- `dietary_restrictions`: Array of strings (optional)
- `allergies`: Array of strings (optional)
- `preferred_cuisine`: String (optional)

**Response:**
```json
{
  "daily_calories": 2100,
  "macronutrients": {
    "protein": 126,
    "carbs": 210,
    "fats": 70,
    "protein_pct": 30,
    "carbs_pct": 40,
    "fats_pct": 30
  },
  "meal_plan": {
    "Monday": {
      "breakfast": "Oatmeal with berries",
      "breakfast_calories": 525,
      "lunch": "Mediterranean salad",
      "lunch_calories": 630,
      "dinner": "Vegetable curry",
      "dinner_calories": 630,
      "snacks": "Greek yogurt with honey",
      "snacks_calories": 315
    },
    "Tuesday": {
      "...": "..."
    },
    "...": "..."
  },
  "hydration": "Drink approximately 2.5 liters of water daily."
}
```

### 3. Weight Tracking API
#### 3.1 Weight Entries (CRUD operations)
**Endpoint:** `/api/weight-entries/`  
**Methods:** GET, POST, PUT, DELETE  
**Authentication:** Required  

**POST Request Body:**
```json
{
  "weight": 78.5,
  "date": "2025-05-20",
  "notes": "After vacation"
}
```

**Parameters:**
- `weight`: Float, weight in kg
- `date`: String, date in YYYY-MM-DD format
- `notes`: String, optional notes (optional)

**GET Response:**
```json
[
  {
    "id": 1,
    "weight": 78.5,
    "date": "2025-05-20",
    "notes": "After vacation",
    "created_at": "2025-05-20T10:30:00Z",
    "updated_at": "2025-05-20T10:30:00Z"
  },
  {
    "...": "..."
  }
]
```

#### 3.2 Weight History with Analysis
**Endpoint:** `/api/weight-history/`  
**Method:** GET  
**Authentication:** Required  

**Response:**
```json
{
  "weight_history": [
    {
      "id": 1,
      "weight": 80.0,
      "date": "2025-05-01",
      "notes": "Starting weight",
      "created_at": "2025-05-01T10:00:00Z",
      "updated_at": "2025-05-01T10:00:00Z"
    },
    {
      "...": "..."
    }
  ],
  "statistics": {
    "average_weight": 79.2,
    "maximum_weight": 80.0,
    "minimum_weight": 78.5,
    "total_entries": 4,
    "date_range": {
      "start": "2025-05-01",
      "end": "2025-05-20"
    },
    "total_change": {
      "kg": -1.5,
      "percentage": -1.88,
      "days": 19
    },
    "weekly_average_change": -0.55
  },
  "trend": {
    "direction": "losing",
    "slope": -0.0789,
    "weekly_change": -0.55,
    "r_squared": 0.9234,
    "confidence": "high"
  },
  "projection": {
    "reliability": "high",
    "based_on_weeks": 2.7,
    "projections": {
      "7_days": {
        "date": "2025-05-27",
        "weight": 77.9,
        "change": -0.6
      },
      "30_days": {
        "date": "2025-06-19",
        "weight": 76.1,
        "change": -2.4
      },
      "90_days": {
        "date": "2025-08-18",
        "weight": 71.4,
        "change": -7.1
      }
    },
    "note": "Projections are estimates based on your current trend and may vary with changes in diet, exercise, or other factors."
  }
}
```

### 4. Model Features API
**Endpoint:** `/api/model-features/`  
**Method:** GET  
**Authentication:** Not required  

**Response:**
```json
{
  "model_version": "1.0.0",
  "features": [
    {
      "name": "Fitness Goal",
      "description": "Primary goal determines overall program structure",
      "importance": 0.95
    },
    {
      "name": "Weight",
      "description": "Current weight used for BMI, caloric needs, and progress tracking",
      "importance": 0.90
    },
    {
      "...": "..."
    }
  ],
  "capabilities": [
    {
      "name": "Weekly Training Structure",
      "description": "Generates personalized weekly workout schedules based on goals and availability"
    },
    {
      "name": "Cardio Training Recommendations",
      "description": "Provides specific cardio exercise recommendations with intensity and duration"
    },
    {
      "...": "..."
    }
  ],
  "accuracy_metrics": {
    "overall_accuracy": 0.89,
    "recommendation_precision": 0.92,
    "user_satisfaction": 0.87,
    "component_accuracy": {
      "weekly_structure": 0.91,
      "cardio_training": 0.88,
      "strength_training": 0.90,
      "progression_plan": 0.85,
      "bmi_guidance": 0.93,
      "age_guidance": 0.89,
      "weight_change": 0.86,
      "cycle_considerations": 0.82
    }
  },
  "last_updated": "2025-05-22"
}
```

## Authentication
All endpoints except the Model Features API require authentication. The application uses token-based authentication.

To authenticate:
1. Obtain a token by sending a POST request to `/api-token-auth/` with your username and password
2. Include the token in the Authorization header of your requests: `Authorization: Token <your_token>`

## Error Handling
The API returns appropriate HTTP status codes:
- 200: Success
- 400: Bad Request (invalid input)
- 401: Unauthorized (authentication required)
- 404: Not Found
- 500: Internal Server Error

Error responses include a message explaining the error:
```json
{
  "error": "Error message details"
}
```

## Rate Limiting
API requests are limited to 100 requests per hour per user to ensure service availability.

## Data Privacy
User data is stored securely and used only for generating personalized recommendations. No personal data is shared with third parties.
