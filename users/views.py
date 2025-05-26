from datetime import date
from datetime import datetime

from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from users.models import User
from users.models import HeightModel, WeightModel

# full_name
# gender
# email
# birthDate
# weight
# height
# activity level
# target_weight
# goal


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class CreateUpdateUserView(APIView):
    """Create user"""

    permission_classes = [AllowAny]  # Allow public access to model information

    def post(self, request):
        """
        {
        'fullName': 'ubsa',
        'gender': 'female',
        'birthDate': '2025-05-21T00:00:00.000',
        'height': 170.0,
        'weight': 85.0,
        'targetWeight': 65.0,
        'goal': 'loseWeight',
        'activityLevel': None,
        'menstrualCycles': ['2025-05-14T00:00:00.000Z', '2025-04-16T00:00:00.000Z', '2025-03-12T00:00:00.000Z'],
        'email': 'insaniyatka@gmail.com',
        'password': 'insA10!'
        }
        """

        activity_level_2 = {"sedentary": 1, "light": 2, "moderate": 3, "active": 4}

        """
            GOALS = [
            (WEIGHT_LOSS, "Похудение"),
            (MAINTENANCE, "Тонус"),
            (WEIGHT_GAIN, "Набор массы"),
            (CUTTING, "Сушка"),
            ]
        """
        goals_2 = {"loseWeight": 1, "maintain": 2, "gainWeight": 3, "cuttin": 4}

        data = request.data
        print("data: ", data)

        user_id = get_random_string(12)
        full_name = data.get("fullName")
        birth_date = data.get("birthDate")

        if birth_date:
            birth_date_dt = datetime.fromisoformat(birth_date)
            age = calculate_age(birth_date_dt)
        else:
            age = 1

        email = data.get("email")

        if data.get("gender") == "male":
            gender = User.MAN
        else:
            gender = User.WOMAN

        goal = goals_2.get(data.get("goal", ""), 1)

        height = data.get("height", 175)
        height = HeightModel(height=height)
        height.save()

        weight = data.get("weight", 80)
        weight = WeightModel(weight=weight)
        weight.save()

        target_weight = data.get("target_weight", 70)

        User.objects.create(
            user_id=user_id,
            full_name=full_name,
            birth_date=birth_date,
            age=age,
            mail=email,
            gender=gender,
            height=height,
            weight=weight,
            target_weight=target_weight,
            goal=goal,
            activity_level=activity_level_2.get(data.get("activityLevel"), 1),
            cycle_record=None,
        )

        return Response({"userId": user_id}, status=200)


class LoginUserView(APIView):
    """Create user"""

    permission_classes = [AllowAny]  # Allow public access to model information

    def post(self, request):
        data = request.data
        print("login user view enter: ", data)
        return Response(status=200)


class ProfileInfoView(APIView):
    permission_classes = [AllowAny]  # Allow public access to model information

    def post(self, request):
        activity_level = {1: "sedentary", 2: "light", 3: "moderate", 4: "active"}
        goals = {1: "loseWeight", 2: "maintain", 3: "gainWeight", 4: "cuttin"}
        """
        ACTIVITY_LEVELS = [
        (SEDENTARY, "Сидячий"),
        (LIGHT_ACTIVITY, "Легкая активность"),
        (MODERATE_ACTIVITY, "Умеренная активность"),
        (VERY_ACTIVE, "Высокая активность"),
        ]
        """
        data = request.data
        print("data: ", data)

        user_id = data.get("userId")
        print("repr: ", repr(user_id))

        if user_id:
            print("iser odL ", user_id)
            for val in get_user_model().objects.all():
                print(repr(val.user_id))
                if val.user_id == user_id:
                    user = val
                    break
            else:
                return Response(status=404)
        else:
            user = get_user_model().objects.last()

        # user = auth_user.objects.filter(user_id=user_id)
        # print("user: ", user)
        print("user: ", user)

        weight = user.weight
        print("weight: ", weight)
        height = user.height

        result = {
            "fullName": user.full_name,
            "gender": "male" if user.gender == 1 else "female",
            "email": user.mail,
            "birthDate": user.birth_date,
            "weight": weight.weight,
            "height": height.height,
            "activity_level": activity_level.get(user.activity_level, "sedentary"),
            "target_weight": user.target_weight,
            "goal": goals.get(user.goal, "loseWeight"),
        }

        return Response(result, status=200)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})
